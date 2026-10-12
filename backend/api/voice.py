"""
backend/api/voice.py
Voice pipeline endpoints for FRIDAY AI Assistant.

Desired flow:
  MICROPHONE → VAD → STT → FRIDAY ROUTER → TOOL/AI → RESPONSE → TTS → SPEAKING

Endpoints:
  GET  /api/voice/status     — current voice pipeline state & config
  GET  /api/voice/devices    — list available audio input devices
  POST /api/voice/speak      — backend TTS playback with speech sanitization
  POST /api/voice/stop       — abort TTS & microphone recording immediately
  POST /api/voice/interrupt  — alias for instant voice interruption
  POST /api/voice/wake-check — text-based wake-word & stop-command detection
  POST /api/voice/transcribe — transcribe an uploaded audio file
  POST /api/voice/listen     — record mic + VAD + STT with timeout bounds
  POST /api/voice/converse   — full end-to-end voice conversation cycle
"""

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import tempfile
import os

from backend.voice.text_to_speech import tts_engine
from backend.voice.speech_to_text import stt_engine
from backend.voice.wake_word import wake_word_detector
from backend.voice.microphone import get_microphone, list_input_devices, get_default_input_device
from backend.database.database import get_db
from backend.database.models import ConversationMessage, ToolAuditLog
from backend.core.agent_router import NaturalLanguageAgent
from backend.config import settings

logger = logging.getLogger("FRIDAY.API.Voice")
router = APIRouter(prefix="/api/voice", tags=["Voice"])

# Thread pool for blocking mic/TTS operations
_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="friday_voice")

# ─── Voice state tracker & WebSocket broadcaster ─────────────────────────────
_voice_state = {"state": "IDLE", "error": None}
_voice_broadcaster = None


def set_voice_broadcaster(fn):
    """Register WebSocket broadcast callback from main.py."""
    global _voice_broadcaster
    _voice_broadcaster = fn


def _set_state(state: str, error: Optional[str] = None):
    _voice_state["state"] = state
    _voice_state["error"] = error
    logger.info("Voice state: %s%s", state, f" ({error})" if error else "")
    if _voice_broadcaster:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_voice_broadcaster(state, error or ""))
        except Exception as e:
            logger.debug("Failed to dispatch voice state broadcast: %s", e)


# ─── Request / Response Models ───────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    async_speak: Optional[bool] = True


class WakeWordCheckRequest(BaseModel):
    text: str


class ConverseRequest(BaseModel):
    session_id: Optional[str] = "default"
    max_seconds: Optional[float] = None
    initial_silence_timeout: Optional[float] = None
    silence_threshold: Optional[float] = None
    speak_response: Optional[bool] = True


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/status")
def voice_status():
    """Return current voice pipeline state and configuration."""
    mic = get_default_input_device()
    return {
        "state": _voice_state["state"],
        "error": _voice_state["error"],
        "enable_voice": settings.ENABLE_VOICE,
        "voice_continuous": settings.VOICE_CONTINUOUS,
        "voice_wakeword_only": settings.VOICE_WAKEWORD_ONLY,
        "recording_timeout": settings.VOICE_RECORDING_TIMEOUT,
        "initial_silence_timeout": settings.VOICE_INITIAL_SILENCE_TIMEOUT,
        "silence_cutoff": settings.VOICE_SILENCE_CUTOFF,
        "rms_threshold": settings.VOICE_RMS_THRESHOLD,
        "is_speaking": tts_engine.is_speaking,
        "voice_info": tts_engine.get_voice_info(),
        "microphone": mic,
    }


@router.get("/devices")
def list_devices():
    """List all available audio input devices."""
    devices = list_input_devices()
    default = get_default_input_device()
    return {"devices": devices, "default": default}


@router.post("/speak")
def speak_endpoint(request: TTSRequest, background_tasks: BackgroundTasks):
    """
    Trigger backend TTS.
    async_speak=True returns immediately while playback occurs in background.
    async_speak=False waits until speech playback finishes.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    _set_state("SPEAKING")

    def _speak_task():
        try:
            tts_engine.speak(request.text)
        except Exception as e:
            logger.error("TTS speech task failed: %s", e, exc_info=True)
            _set_state("ERROR", str(e))
        finally:
            _set_state("IDLE")

    if request.async_speak:
        background_tasks.add_task(_speak_task)
        return {"status": "speaking_queued", "text": request.text}
    else:
        success = False
        try:
            success = tts_engine.speak(request.text)
        except Exception as e:
            logger.error("TTS synchronous speak error: %s", e, exc_info=True)
            _set_state("ERROR", str(e))
        finally:
            _set_state("IDLE")
        return {"status": "completed" if success else "failed", "text": request.text}


@router.post("/stop")
def stop_endpoint():
    """Immediately stop TTS playback and microphone recording."""
    mic = get_microphone()
    mic.stop()
    tts_engine.stop()
    _set_state("IDLE")
    logger.info("Voice pipeline: stop invoked successfully.")
    return {"status": "stopped", "message": "Microphone and speech playback halted."}


@router.post("/interrupt")
def interrupt_endpoint():
    """Alias for stopping active speech and returning to idle/listening."""
    return stop_endpoint()


@router.post("/wake-check")
def wake_check_endpoint(request: WakeWordCheckRequest):
    """Check if input text contains a wake-word or stop-command phrase."""
    detected = wake_word_detector.detect_in_text(request.text)
    is_stop = wake_word_detector.detect_stop_command(request.text)
    return {
        "text": request.text,
        "wake_word_detected": detected,
        "phrase": "FRIDAY" if detected else None,
        "is_stop_command": is_stop,
    }


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file using the backend STT engine."""
    tmp_path = None
    try:
        suffix = "." + file.filename.split(".")[-1] if file.filename and "." in file.filename else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        transcription = stt_engine.transcribe_audio_file(tmp_path)
        if transcription:
            is_stop = wake_word_detector.detect_stop_command(transcription)
            return {"status": "success", "transcription": transcription, "is_stop_command": is_stop}
        else:
            return {"status": "no_speech", "transcription": None, "is_stop_command": False}
    except Exception as e:
        logger.error("File transcription endpoint failure: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@router.post("/listen")
async def listen_endpoint():
    """
    Record from the default microphone until an utterance ends, then transcribe.
    Non-blocking to the main event loop (executed in dedicated thread pool).

    Flow:
      1. Open microphone stream with VAD
      2. Detect speech start / end automatically
      3. Run STT on the captured audio
      4. Detect stop/interruption commands
      5. Return transcription text

    State transitions: IDLE → LISTENING → THINKING → IDLE/ERROR
    """
    mic = get_microphone()

    if _voice_state["state"] in ("LISTENING", "SPEAKING"):
        return {
            "status": "busy",
            "transcription": None,
            "error": f"Voice pipeline is currently {_voice_state['state']}.",
        }

    _set_state("LISTENING")
    logger.info("Microphone: Starting voice capture session.")

    try:
        loop = asyncio.get_event_loop()
        audio_np, sr = await loop.run_in_executor(
            _executor,
            lambda: mic.record_utterance(
                silence_threshold=settings.VOICE_RMS_THRESHOLD,
                silence_cutoff_blocks=int(settings.VOICE_SILENCE_CUTOFF * 16000 / 512),
                max_seconds=settings.VOICE_RECORDING_TIMEOUT,
                initial_silence_timeout=settings.VOICE_INITIAL_SILENCE_TIMEOUT,
            )
        )
    except Exception as e:
        _set_state("ERROR", str(e))
        logger.error("Microphone capture failed with exception: %s", e, exc_info=True)
        return {"status": "error", "transcription": None, "error": str(e)}

    if audio_np is None:
        _set_state("IDLE")
        return {"status": "no_speech", "transcription": None, "error": "No speech detected within timeout."}

    _set_state("THINKING")
    logger.info("STT: Speech audio captured; running transcription.")

    try:
        transcription = await loop.run_in_executor(
            _executor,
            lambda: stt_engine.transcribe_numpy_array(audio_np, sample_rate=sr),
        )
    except Exception as e:
        _set_state("ERROR", str(e))
        logger.error("STT recognition failed: %s", e, exc_info=True)
        return {"status": "error", "transcription": None, "error": str(e)}

    _set_state("IDLE")

    if not transcription:
        return {
            "status": "unintelligible",
            "transcription": None,
            "error": "Speech was detected but could not be recognized."
        }

    is_stop = wake_word_detector.detect_stop_command(transcription)
    if is_stop:
        logger.info("Voice stop command detected in transcription: '%s'", transcription)
        tts_engine.stop()

    logger.info("STT recognized utterance: '%s'", transcription)
    return {
        "status": "success",
        "transcription": transcription,
        "is_stop_command": is_stop,
        "error": None
    }


@router.post("/converse")
async def converse_endpoint(
    req: ConverseRequest = ConverseRequest(),
    db: Session = Depends(get_db)
):
    """
    Complete continuous voice conversation cycle:
    MICROPHONE → VAD → STT → FRIDAY ROUTER → TOOL/AI → RESPONSE → TTS → SPEAKING

    Returns:
      {
        "status": "success" | "no_speech" | "interrupted" | "unintelligible" | "error" | "busy",
        "transcription": str,
        "response": str,
        "mode": str,
        "tool_calls": list
      }
    """
    mic = get_microphone()
    if _voice_state["state"] in ("LISTENING", "SPEAKING"):
        return {
            "status": "busy",
            "transcription": None,
            "response": None,
            "error": f"Voice pipeline is currently {_voice_state['state']}."
        }

    loop = asyncio.get_event_loop()

    # 1. MICROPHONE + VAD (LISTENING)
    _set_state("LISTENING")
    max_sec = req.max_seconds or settings.VOICE_RECORDING_TIMEOUT
    init_timeout = req.initial_silence_timeout or settings.VOICE_INITIAL_SILENCE_TIMEOUT
    rms_thresh = req.silence_threshold or settings.VOICE_RMS_THRESHOLD

    try:
        audio_np, sr = await loop.run_in_executor(
            _executor,
            lambda: mic.record_utterance(
                silence_threshold=rms_thresh,
                silence_cutoff_blocks=int(settings.VOICE_SILENCE_CUTOFF * 16000 / 512),
                max_seconds=max_sec,
                initial_silence_timeout=init_timeout,
            )
        )
    except Exception as e:
        _set_state("ERROR", str(e))
        logger.error("Converse mic error: %s", e, exc_info=True)
        return {"status": "error", "error": f"Microphone error: {str(e)}"}

    if audio_np is None:
        _set_state("IDLE")
        return {"status": "no_speech", "transcription": None, "response": None}

    # 2. STT (THINKING)
    _set_state("THINKING")
    try:
        transcription = await loop.run_in_executor(
            _executor,
            lambda: stt_engine.transcribe_numpy_array(audio_np, sample_rate=sr),
        )
    except Exception as e:
        _set_state("ERROR", str(e))
        logger.error("Converse STT error: %s", e, exc_info=True)
        return {"status": "error", "error": f"STT error: {str(e)}"}

    if not transcription or not transcription.strip():
        _set_state("IDLE")
        return {"status": "unintelligible", "transcription": None, "response": None}

    # 3. INTERRUPT / STOP COMMAND CHECK
    if wake_word_detector.detect_stop_command(transcription):
        logger.info("Voice stop command triggered during conversation: '%s'", transcription)
        tts_engine.stop()
        _set_state("IDLE")
        return {
            "status": "interrupted",
            "transcription": transcription,
            "response": "Understood, sir. Halting voice activity.",
            "mode": "voice_interrupted",
            "tool_calls": None
        }

    # 4. WAKE-WORD FILTERING (IF CONFIGURED)
    query_text = transcription
    if settings.VOICE_WAKEWORD_ONLY:
        if not wake_word_detector.detect_in_text(transcription):
            _set_state("IDLE")
            return {
                "status": "ignored_no_wakeword",
                "transcription": transcription,
                "response": None,
                "mode": "wakeword_required"
            }
        query_text = wake_word_detector.strip_wake_word(transcription)
        if not query_text:
            query_text = "Hello"

    # 5. FRIDAY ROUTER → TOOL / AI → RESPONSE
    try:
        # Record user message in DB
        user_msg_db = ConversationMessage(
            session_id=req.session_id or "default",
            role="user",
            content=query_text
        )
        db.add(user_msg_db)
        db.commit()

        # Process with natural language agent router
        agent_result = NaturalLanguageAgent.process_request(
            user_message=query_text,
            session_id=req.session_id or "default",
            db=db
        )
        assistant_response = agent_result.get("response", "Request processed, sir.")
        response_mode = agent_result.get("mode", "friday_voice")
        tool_calls = agent_result.get("tool_calls") or []

        # Audit tools if any
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name") or tool_call.get("name") or "tool"
            audit = ToolAuditLog(
                tool_name=tool_name,
                arguments=tool_call.get("arguments"),
                result=str(tool_call.get("result") or tool_call.get("message") or ""),
                status=tool_call.get("status", "SUCCESS")
            )
            db.add(audit)

        # Record assistant reply in DB
        assistant_msg_db = ConversationMessage(
            session_id=req.session_id or "default",
            role="assistant",
            content=assistant_response
        )
        db.add(assistant_msg_db)
        db.commit()

    except Exception as e:
        _set_state("ERROR", str(e))
        logger.error("FRIDAY Router error during voice request: %s", e, exc_info=True)
        return {
            "status": "error",
            "transcription": transcription,
            "error": f"Agent router error: {str(e)}"
        }

    # 6. TTS → SPEAKING
    if req.speak_response and assistant_response:
        _set_state("SPEAKING")
        try:
            await loop.run_in_executor(
                _executor,
                lambda: tts_engine.speak(assistant_response)
            )
        except Exception as e:
            logger.error("TTS playback error in converse endpoint: %s", e, exc_info=True)
        finally:
            _set_state("IDLE")
    else:
        _set_state("IDLE")

    return {
        "status": "success",
        "transcription": transcription,
        "response": assistant_response,
        "mode": response_mode,
        "tool_calls": tool_calls
    }
