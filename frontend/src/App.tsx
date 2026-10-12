import React, { useState, useEffect, useRef, useCallback } from 'react';
import { HolographicCore } from './components/HolographicCore';
import type { AssistantState } from './components/AIReactor';
import { HUDHeader } from './components/HUDHeader';
import { TelemetryPanel } from './components/TelemetryPanel';
import type { SystemStatsData } from './components/SystemStats';
import { ActivityLogPanel } from './components/ActivityLogPanel';
import type { ToolLog } from './components/ToolActivity';
import { ConversationDeck } from './components/ConversationDeck';
import type { ChatMessage } from './components/ChatPanel';
import { MemoryExplorer } from './components/MemoryExplorer';
import type { MemoryItemData } from './components/MemoryExplorer';
import { SettingsModal } from './components/SettingsModal';
import { Waveform } from './components/Waveform';

const API_BASE = 'http://127.0.0.1:8000';

export const App: React.FC = () => {
  const [assistantState, setAssistantState] = useState<AssistantState>('IDLE');
  const [statusText, setStatusText] = useState('SYSTEMS OPERATIONAL — AWAITING COMMAND');
  const [activeToolName, setActiveToolName] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStatsData | null>(null);
  const [toolLogs, setToolLogs] = useState<ToolLog[]>([]);
  const [memories, setMemories] = useState<MemoryItemData[]>([]);
  const [pendingConfirmation, setPendingConfirmation] = useState<ToolLog | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isMemoryOpen, setIsMemoryOpen] = useState(false);
  const [wakeDetected, setWakeDetected] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [config, setConfig] = useState({
    openai_api_key_masked: '',
    openai_model: 'gpt-4o',
    enable_voice: true,
    safe_mode: true,
    voice_continuous: true,
    voice_wakeword_only: false,
  });

  // Continuous voice loop control
  const continuousRef = useRef(false);
  const listeningAbortRef = useRef(false);

  // ── System Stats Polling ───────────────────────────────────────────────────
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/system/stats`);
        if (res.ok) setSystemStats(await res.json());
      } catch {}
    };
    fetchStats();
    const iv = setInterval(fetchStats, 3000);
    return () => clearInterval(iv);
  }, []);

  // ── Startup Initialization ────────────────────────────────────────────────
  useEffect(() => {
    fetchMemories();
    fetchConfig();
    fetchToolLogs();
    setMessages([{
      id: 'welcome-1',
      role: 'assistant',
      content: 'Good day, sir. FRIDAY is online. How may I assist you?',
      timestamp: new Date().toLocaleTimeString(),
    }]);
  }, []);

  // ── WebSocket — receive real-time voice state ──────────────────────────────
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      try {
        ws = new WebSocket('ws://127.0.0.1:8000/ws');
        ws.onmessage = (evt) => {
          try {
            const data = JSON.parse(evt.data);
            if (data.type === 'voice_state') {
              const s = data.state as AssistantState;
              setAssistantState(s);
              if (s === 'ERROR' && data.detail) {
                setVoiceError(data.detail);
              }
            }
          } catch {}
        };
        ws.onclose = () => {
          reconnectTimer = setTimeout(connect, 3000);
        };
      } catch {}
    };

    connect();
    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, []);

  const fetchMemories = async () => { try { const r = await fetch(`${API_BASE}/api/memory`); if (r.ok) setMemories(await r.json()); } catch {} };
  const fetchToolLogs = async () => { try { const r = await fetch(`${API_BASE}/api/tools/audit`); if (r.ok) setToolLogs(await r.json()); } catch {} };
  const fetchConfig   = async () => { try { const r = await fetch(`${API_BASE}/api/system/config`); if (r.ok) setConfig(await r.json()); } catch {} };

  // ── TTS — speak via backend ───────────────────────────────────────────────
  const speakText = useCallback(async (text: string) => {
    if (!soundEnabled || !config.enable_voice) return;
    setAssistantState('SPEAKING');

    // Trigger backend TTS on physical audio output
    try {
      await fetch(`${API_BASE}/api/voice/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, async_speak: true }),
      });
    } catch {}
  }, [soundEnabled, config.enable_voice]);

  // ── Stop Speaking / Interruption ──────────────────────────────────────────
  const handleStopSpeaking = useCallback(async () => {
    // Cancel browser synthesis
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();

    // Cancel backend TTS + mic
    try {
      await fetch(`${API_BASE}/api/voice/stop`, { method: 'POST' });
    } catch {}

    // Cancel continuous loop
    listeningAbortRef.current = true;
    continuousRef.current = false;
    setIsListening(false);
    setAssistantState('IDLE');
    setStatusText('SYSTEMS OPERATIONAL — AWAITING COMMAND');
  }, []);

  // ── Core Send-Message Pipeline ─────────────────────────────────────────────
  const handleSendMessage = useCallback(async (text: string) => {
    if (!text || !text.trim()) return;

    // Optional wake-word check
    try {
      const wr = await fetch(`${API_BASE}/api/voice/wake-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (wr.ok) {
        const wd = await wr.json();
        if (wd.wake_word_detected) {
          setWakeDetected(true);
          setTimeout(() => setWakeDetected(false), 4000);
        }
      }
    } catch {}

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setAssistantState('THINKING');
    setStatusText(`PROCESSING REQUEST: "${text}"`);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) throw new Error('Backend error');

      const data = await res.json();
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toLocaleTimeString(),
        mode: data.mode,
      };
      setMessages(prev => [...prev, assistantMsg]);
      await speakText(data.response);
      setStatusText('SYSTEMS OPERATIONAL');

      if (data.tool_calls?.length) {
        for (const tc of data.tool_calls) {
          const tName = tc.tool_name || tc.name;
          if (tc.status === 'CONFIRMATION_REQUIRED') {
            setPendingConfirmation({
              id: Date.now().toString(),
              tool_name: tName,
              status: 'CONFIRMATION_REQUIRED',
              timestamp: new Date().toLocaleTimeString(),
              arguments: tc.arguments,
              details: tc.message || 'Requires user confirmation',
            });
          }
        }
      }

      if (data.mode === 'memory_engine' || text.toLowerCase().includes('remember') || text.toLowerCase().includes('forget')) {
        fetchMemories();
      }
      fetchToolLogs();

    } catch {
      setAssistantState('ERROR');
      setStatusText('ERROR CONNECTING TO BACKEND');
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, sir. I encountered a communication error. Please check that the server is running.',
        timestamp: new Date().toLocaleTimeString(),
      }]);
    }
  }, [speakText]);

  // ── Backend-Driven Voice Listen Loop ───────────────────────────────────────
  const runListenCycle = useCallback(async () => {
    if (listeningAbortRef.current) return;

    setAssistantState('LISTENING');
    setStatusText('LISTENING FOR VOICE COMMAND...');
    setVoiceError(null);

    try {
      const res = await fetch(`${API_BASE}/api/voice/listen`, {
        method: 'POST',
      });

      if (listeningAbortRef.current) return;

      if (!res.ok) {
        const err = await res.text();
        setVoiceError(`Microphone error: ${err}`);
        setAssistantState('ERROR');
        setStatusText('MICROPHONE ERROR');
        setIsListening(false);
        continuousRef.current = false;
        return;
      }

      const data = await res.json();

      if (listeningAbortRef.current) return;

      if (data.status === 'success' && data.transcription) {
        const transcript = data.transcription as string;
        setStatusText(`RECOGNIZED: "${transcript}"`);

        // Check if transcription is an explicit stop/interruption command
        if (data.is_stop_command) {
          setStatusText('VOICE STOP COMMAND — HALTING SPEECH');
          handleStopSpeaking();
          return;
        }

        // In wake-word-only mode, only proceed if wake phrase present
        if (config.voice_wakeword_only) {
          const wakeRes = await fetch(`${API_BASE}/api/voice/wake-check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: transcript }),
          });
          const wakeData = wakeRes.ok ? await wakeRes.json() : { wake_word_detected: false };
          if (!wakeData.wake_word_detected) {
            // Not a wake-word utterance; loop back to listening
            if (continuousRef.current && !listeningAbortRef.current) {
              setTimeout(runListenCycle, 200);
            }
            return;
          }
          // Wake word detected — acknowledge
          setWakeDetected(true);
          setTimeout(() => setWakeDetected(false), 4000);
          await speakText("Yes, sir?");
          // Listen once more for the actual command
          const cmdRes = await fetch(`${API_BASE}/api/voice/listen`, { method: 'POST' });
          const cmdData = cmdRes.ok ? await cmdRes.json() : null;
          if (cmdData?.status === 'success' && cmdData.transcription) {
            await handleSendMessage(cmdData.transcription);
          }
        } else {
          await handleSendMessage(transcript);
        }
      } else if (data.status === 'no_speech') {
        // Silence — loop back cleanly without showing error
        setStatusText('SYSTEMS OPERATIONAL — AWAITING COMMAND');
      } else if (data.status === 'unintelligible') {
        setStatusText('COULD NOT RECOGNIZE SPEECH');
        await speakText("I did not catch that, sir. Could you please repeat?");
      } else if (data.status === 'busy') {
        await new Promise(r => setTimeout(r, 1000));
      } else if (data.status === 'error') {
        setVoiceError(data.error || 'Unknown microphone error');
        setAssistantState('ERROR');
        setStatusText('MICROPHONE ERROR');
        setIsListening(false);
        continuousRef.current = false;
        return;
      }
    } catch (err) {
      if (!listeningAbortRef.current) {
        setVoiceError('Could not reach backend voice service.');
        setAssistantState('ERROR');
        setStatusText('VOICE SERVICE UNAVAILABLE');
        setIsListening(false);
        continuousRef.current = false;
        return;
      }
    }

    // Continuous mode: start next cycle after brief pause
    if (continuousRef.current && !listeningAbortRef.current) {
      setTimeout(runListenCycle, 300);
    } else {
      setIsListening(false);
      setAssistantState('IDLE');
      setStatusText('SYSTEMS OPERATIONAL — AWAITING COMMAND');
    }
  }, [config.voice_wakeword_only, handleSendMessage, handleStopSpeaking, speakText]);

  // ── Toggle Voice Listening ────────────────────────────────────────────────
  const toggleListening = useCallback(() => {
    if (isListening) {
      listeningAbortRef.current = true;
      continuousRef.current = false;
      setIsListening(false);
      setAssistantState('IDLE');
      setStatusText('SYSTEMS OPERATIONAL — AWAITING COMMAND');
      fetch(`${API_BASE}/api/voice/stop`, { method: 'POST' }).catch(() => {});
    } else {
      listeningAbortRef.current = false;
      continuousRef.current = config.voice_continuous;
      setIsListening(true);
      runListenCycle();
    }
  }, [isListening, config.voice_continuous, runListenCycle]);

  // ── Tool Confirmations ─────────────────────────────────────────────────────
  const handleConfirmTool = async (log: ToolLog) => {
    setPendingConfirmation(null);
    setAssistantState('EXECUTING');
    setActiveToolName(log.tool_name);
    setStatusText(`EXECUTING APPROVED TOOL: ${log.tool_name}...`);
    try {
      const res = await fetch(`${API_BASE}/api/tools/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_name: log.tool_name, arguments: log.arguments || {}, bypass_security: true }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: `[TOOL APPROVED & EXECUTED]: ${log.tool_name} completed — ${data.result ? JSON.stringify(data.result) : (data.error || 'Done')}`,
        timestamp: new Date().toLocaleTimeString(),
        mode: 'security_approved',
      }]);
      speakText(`Tool ${log.tool_name} executed successfully.`);
      fetchToolLogs();
    } catch {
      setAssistantState('ERROR');
      setStatusText('ERROR EXECUTING CONFIRMED TOOL');
    } finally {
      setActiveToolName(null);
      setAssistantState('IDLE');
    }
  };

  const handleRejectTool = (log: ToolLog) => {
    setPendingConfirmation(null);
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'assistant',
      content: `[ACTION REJECTED]: Execution of '${log.tool_name}' denied.`,
      timestamp: new Date().toLocaleTimeString(),
      mode: 'security_rejected',
    }]);
    speakText("Action cancelled, sir.");
  };

  // ── Vision Trigger ─────────────────────────────────────────────────────────
  const handleTriggerVision = async () => {
    setAssistantState('THINKING');
    setStatusText('CAPTURING & ANALYZING DISPLAY...');
    try {
      const res = await fetch(`${API_BASE}/api/vision/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: "What is currently displayed on screen?" }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: `[DESKTOP VISION]: ${data.analysis || data.summary || 'Display analyzed.'}`,
          timestamp: new Date().toLocaleTimeString(),
          mode: 'vision_analytics',
        }]);
        speakText(data.analysis || data.summary || "Display analyzed.");
      }
    } catch {
      setAssistantState('ERROR');
      setStatusText('VISION ANALYSIS FAILED');
    } finally {
      setAssistantState('IDLE');
    }
  };

  // ── Multi-Step Agent Planner Trigger ───────────────────────────────────────
  const handleTriggerAgent = async (query: string) => {
    setAssistantState('EXECUTING');
    setActiveToolName('AGENT PLANNER');
    setStatusText(`AGENT PLANNER RUNNING: "${query}"...`);
    try {
      const res = await fetch(`${API_BASE}/api/agent/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: `[AGENT PLANNER COMPLETED]: ${data.summary || data.plan || 'Task executed.'}`,
          timestamp: new Date().toLocaleTimeString(),
          mode: 'multi_step_agent',
        }]);
        speakText(data.summary || "Agent task finished successfully.");
        fetchToolLogs();
      }
    } catch {
      setAssistantState('ERROR');
      setStatusText('ERROR IN AGENT EXECUTION');
    } finally {
      setActiveToolName(null);
      setAssistantState('IDLE');
    }
  };

  // ── Render Complete HUD ────────────────────────────────────────────────────
  return (
    <div className="h-screen w-screen bg-[#040507] text-slate-100 flex flex-col overflow-hidden font-ui">
      {/* HUD Header */}
      <HUDHeader
        assistantState={assistantState}
        soundEnabled={soundEnabled}
        onToggleSound={() => setSoundEnabled(!soundEnabled)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onToggleMemory={() => setIsMemoryOpen(!isMemoryOpen)}
        safeMode={config.safe_mode}
        voiceContinuous={config.voice_continuous}
        voiceError={voiceError}
        networkOnline={systemStats?.network.online ?? true}
      />

      {/* Main HUD Layout Grid */}
      <main className="flex-1 p-3 grid grid-cols-1 lg:grid-cols-12 gap-3 overflow-hidden">
        
        {/* LEFT COLUMN: Hardware Telemetry (3 cols) */}
        <div className="lg:col-span-3 flex flex-col h-full overflow-hidden">
          {isMemoryOpen ? (
            <MemoryExplorer
              memories={memories}
              onAddMemory={async (key, value) => {
                await fetch(`${API_BASE}/api/memory`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key, value }) });
                fetchMemories();
              }}
              onDeleteMemory={async (id) => {
                await fetch(`${API_BASE}/api/memory/${id}`, { method: 'DELETE' });
                fetchMemories();
              }}
              onSearch={async (q) => {
                if (!q) { fetchMemories(); return; }
                const r = await fetch(`${API_BASE}/api/memory/search?query=${q}`);
                if (r.ok) setMemories(await r.json());
              }}
              onClose={() => setIsMemoryOpen(false)}
            />
          ) : (
            <TelemetryPanel stats={systemStats} />
          )}
        </div>

        {/* CENTER COLUMN: The Holographic Spherical AI Core (5 cols) */}
        <div className="lg:col-span-5 flex flex-col h-full justify-between overflow-hidden">
          <div className="hud-panel flex-1 flex flex-col items-center justify-center relative p-4">
            <HolographicCore
              state={assistantState}
              statusText={statusText}
              activeToolName={activeToolName}
              wakeDetected={wakeDetected}
            />
            {/* Waveform under core */}
            <div className="w-full max-w-xs mt-1">
              <Waveform state={assistantState} />
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Activity / Tool Log (4 cols) */}
        <div className="lg:col-span-4 flex flex-col h-full overflow-hidden">
          <ActivityLogPanel
            logs={toolLogs}
            pendingConfirmation={pendingConfirmation}
            onConfirmTool={handleConfirmTool}
            onRejectTool={handleRejectTool}
          />
        </div>

        {/* BOTTOM FULL-WIDTH: Live Conversation Feed & Command Deck */}
        <div className="lg:col-span-12 h-64 overflow-hidden">
          <ConversationDeck
            messages={messages}
            onSendMessage={handleSendMessage}
            onVoiceToggle={toggleListening}
            onStopSpeaking={handleStopSpeaking}
            isListening={isListening}
            isSpeaking={assistantState === 'SPEAKING'}
            onTriggerVision={handleTriggerVision}
            onTriggerAgent={handleTriggerAgent}
          />
        </div>
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentSettings={config}
        onSave={async (newSettings) => {
          await fetch(`${API_BASE}/api/system/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              openai_api_key: newSettings.apiKey,
              openai_model: newSettings.model,
              enable_voice: newSettings.voice,
              safe_mode: newSettings.safeMode,
              voice_continuous: newSettings.voiceContinuous,
              voice_wakeword_only: newSettings.voiceWakewordOnly,
            }),
          });
          fetchConfig();
        }}
      />
    </div>
  );
};

export default App;
