"""
backend/voice/microphone.py
Real microphone capture with software Voice Activity Detection (VAD) for FRIDAY.
"""

import logging
import threading
import queue
from typing import Optional, Tuple, List, Dict
import numpy as np

try:
    from backend.config import settings
except ImportError:
    settings = None

logger = logging.getLogger("FRIDAY.Voice.Microphone")

SAMPLE_RATE = 16000
BLOCK_SIZE  = 512
CHANNELS    = 1
DTYPE       = "float32"

SPEECH_RMS_THRESHOLD    = getattr(settings, "VOICE_RMS_THRESHOLD", 0.015) if settings else 0.015
SILENCE_BLOCKS_CUTOFF   = int((getattr(settings, "VOICE_SILENCE_CUTOFF", 1.2) if settings else 1.2) * SAMPLE_RATE / BLOCK_SIZE)
MAX_RECORD_SECONDS      = getattr(settings, "VOICE_RECORDING_TIMEOUT", 15.0) if settings else 15.0
INITIAL_SILENCE_TIMEOUT = getattr(settings, "VOICE_INITIAL_SILENCE_TIMEOUT", 5.0) if settings else 5.0
PRE_SPEECH_BLOCKS       = getattr(settings, "VOICE_PRE_SPEECH_BLOCKS", 5) if settings else 5


def list_input_devices() -> List[Dict]:
    """Return all available audio input devices."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        result = []
        for idx, d in enumerate(devices):
            if d.get("max_input_channels", 0) > 0:
                result.append({
                    "index": idx,
                    "name": d.get("name", f"Device #{idx}"),
                    "default_samplerate": int(d.get("default_samplerate", SAMPLE_RATE)),
                    "channels": d.get("max_input_channels", 1),
                })
        logger.debug("Discovered %d audio input devices.", len(result))
        return result
    except Exception as e:
        logger.error("Failed to query audio devices: %s", e, exc_info=True)
        return []


def get_default_input_device() -> Optional[Dict]:
    """Return information about the default input device, or None."""
    try:
        import sounddevice as sd
        idx = sd.default.device[0]
        if idx is None or idx < 0:
            logger.warning("No default input device configured in sounddevice.")
            return None
        d = sd.query_devices(idx)
        return {
            "index": idx,
            "name": d.get("name", f"Device #{idx}"),
            "default_samplerate": int(d.get("default_samplerate", SAMPLE_RATE)),
            "channels": d.get("max_input_channels", 1),
        }
    except Exception as e:
        logger.error("Failed to query default input device: %s", e, exc_info=True)
        return None


class MicrophoneCapture:
    """
    Captures one utterance from the microphone using VAD-based segmentation.
    Thread-safe: only one recording session runs at a time.
    Guarantees:
      - Never records indefinitely: bounded by initial silence timeout and max duration.
      - Low-latency real-time cancellation via stop().
      - Detailed structured error logging on any audio hardware/driver failure.
    """

    def __init__(self, device: Optional[int] = None):
        self._device = device
        self._recording_lock = threading.Lock()
        self._stop_requested = False
        self._active_stream = None

    @property
    def is_recording(self) -> bool:
        """True if a recording session is currently acquiring audio."""
        return self._recording_lock.locked()

    def stop(self):
        """Abort an in-progress recording session immediately."""
        self._stop_requested = True
        logger.info("Microphone: stop requested by caller.")
        try:
            if self._active_stream:
                self._active_stream.stop()
        except Exception as e:
            logger.debug("Error while stopping active stream: %s", e)

    def record_utterance(
        self,
        silence_threshold: Optional[float] = None,
        silence_cutoff_blocks: Optional[int] = None,
        max_seconds: Optional[float] = None,
        initial_silence_timeout: Optional[float] = None,
    ) -> Tuple[Optional[np.ndarray], int]:
        """
        Record until speech ends, initial silence timeout is exceeded, or max_seconds is reached.
        Returns (audio_float32_array, sample_rate) or (None, sample_rate).
        """
        threshold = silence_threshold if silence_threshold is not None else SPEECH_RMS_THRESHOLD
        cutoff_blocks = silence_cutoff_blocks if silence_cutoff_blocks is not None else SILENCE_BLOCKS_CUTOFF
        max_sec = max_seconds if max_seconds is not None else MAX_RECORD_SECONDS
        init_timeout = initial_silence_timeout if initial_silence_timeout is not None else INITIAL_SILENCE_TIMEOUT

        if not self._recording_lock.acquire(blocking=False):
            logger.warning("Microphone: capture skipped — recording is already active in another thread.")
            return None, SAMPLE_RATE

        self._stop_requested = False

        try:
            import sounddevice as sd
        except ImportError:
            logger.error("Microphone initialization failure: sounddevice package is not installed.")
            self._recording_lock.release()
            return None, SAMPLE_RATE

        audio_q: queue.Queue = queue.Queue()

        def _callback(indata, frames, time_info, status):
            if status:
                logger.warning("Microphone stream status warning: %s", status)
            audio_q.put(indata.copy())

        try:
            stream = sd.InputStream(
                device=self._device,
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                blocksize=BLOCK_SIZE,
                callback=_callback,
            )
            self._active_stream = stream
        except Exception as e:
            logger.error("Failed to initialize microphone InputStream on device %s: %s", self._device, e, exc_info=True)
            self._recording_lock.release()
            self._active_stream = None
            return None, SAMPLE_RATE

        logger.info(
            "Microphone: listening started (RMS threshold=%.4f, silence cutoff=%d blocks, max_sec=%.1f, initial_timeout=%.1f).",
            threshold, cutoff_blocks, max_sec, init_timeout
        )

        all_blocks: List[np.ndarray] = []
        pre_speech_buffer: List[np.ndarray] = []
        speech_started = False
        silent_block_count = 0
        total_blocks_processed = 0

        max_blocks = int(max_sec * SAMPLE_RATE / BLOCK_SIZE)
        initial_silence_blocks = int(init_timeout * SAMPLE_RATE / BLOCK_SIZE)

        try:
            with stream:
                while not self._stop_requested:
                    try:
                        block = audio_q.get(timeout=1.5)
                    except queue.Empty:
                        logger.warning("Microphone: audio queue read timeout (no audio stream incoming).")
                        break

                    total_blocks_processed += 1
                    rms = float(np.sqrt(np.mean(block ** 2)))

                    if rms >= threshold:
                        if not speech_started:
                            logger.info("Microphone: speech onset detected (RMS=%.4f >= threshold=%.4f).", rms, threshold)
                            speech_started = True
                            all_blocks.extend(pre_speech_buffer)
                            pre_speech_buffer.clear()
                        silent_block_count = 0
                        all_blocks.append(block)

                        if len(all_blocks) >= max_blocks:
                            logger.info("Microphone: maximum speech recording duration reached (%d blocks).", max_blocks)
                            break
                    else:
                        if speech_started:
                            all_blocks.append(block)
                            silent_block_count += 1
                            if silent_block_count >= cutoff_blocks:
                                logger.info(
                                    "Microphone: speech concluded after %d consecutive silent blocks (%.2fs silence).",
                                    silent_block_count, silent_block_count * BLOCK_SIZE / SAMPLE_RATE
                                )
                                break
                            if len(all_blocks) >= max_blocks:
                                logger.info("Microphone: maximum recording duration reached during speech.")
                                break
                        else:
                            # Pre-speech silence
                            pre_speech_buffer.append(block)
                            if len(pre_speech_buffer) > PRE_SPEECH_BLOCKS:
                                pre_speech_buffer.pop(0)

                            if total_blocks_processed >= initial_silence_blocks:
                                logger.info(
                                    "Microphone: initial silence timeout reached (%d blocks / %.1fs) without speech.",
                                    total_blocks_processed, init_timeout
                                )
                                break

        except Exception as e:
            logger.error("Microphone recording runtime error: %s", e, exc_info=True)
            return None, SAMPLE_RATE
        finally:
            self._active_stream = None
            self._recording_lock.release()

        if self._stop_requested:
            logger.info("Microphone: recording session was explicitly aborted.")
            return None, SAMPLE_RATE

        if not speech_started or not all_blocks:
            logger.info("Microphone: no valid speech captured during recording session.")
            return None, SAMPLE_RATE

        audio_np = np.concatenate(all_blocks, axis=0).flatten()
        duration = len(audio_np) / SAMPLE_RATE
        logger.info("Microphone: successfully captured %.2f seconds of speech audio.", duration)
        return audio_np, SAMPLE_RATE


_mic_capture = MicrophoneCapture()


def get_microphone() -> MicrophoneCapture:
    return _mic_capture
