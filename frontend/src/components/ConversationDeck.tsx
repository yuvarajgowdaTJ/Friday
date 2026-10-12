import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Camera, Sparkles, StopCircle, User, Bot, Terminal } from 'lucide-react';
import type { ChatMessage } from './ChatPanel';

interface ConversationDeckProps {
  messages: ChatMessage[];
  onSendMessage: (msg: string) => void;
  onVoiceToggle: () => void;
  onStopSpeaking: () => void;
  isListening: boolean;
  isSpeaking: boolean;
  onTriggerVision: () => void;
  onTriggerAgent: (query: string) => void;
}

export const ConversationDeck: React.FC<ConversationDeckProps> = ({
  messages,
  onSendMessage,
  onVoiceToggle,
  onStopSpeaking,
  isListening,
  isSpeaking,
  onTriggerVision,
  onTriggerAgent,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSendMessage(input);
    setInput('');
  };

  const handleAgentClick = () => {
    if (!input.trim()) return;
    onTriggerAgent(input);
    setInput('');
  };

  return (
    <div className="hud-panel flex flex-col h-full select-none">
      {/* ── Header Bar: Communication Channel Status & Controls ──────────────── */}
      <div className="px-4 py-2 border-b border-cyan-500/20 flex justify-between items-center bg-[#000205]/70">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-cyan-400" />
          <div>
            <span className="font-display text-xs tracking-[0.2em] text-cyan-100 uppercase glow-text-cyan leading-none">
              FRIDAY COMMUNICATION CHANNEL
            </span>
            <span className="hidden sm:inline-block ml-2 font-mono text-[8px] tracking-wider text-cyan-400/60 uppercase">
              SECURE AI CONVERSATION STREAM
            </span>
          </div>
        </div>

        {/* Center/Right Dynamic Voice & Channel State */}
        <div className="flex items-center space-x-2">
          {/* Real-time Voice State Badge */}
          {isSpeaking ? (
            <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/70 border border-cyan-400/60 text-cyan-200 font-mono text-[10px] shadow-[0_0_12px_rgba(0,243,255,0.35)] animate-pulse">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-300 animate-ping" />
              <span className="font-bold tracking-wider">◉ SPEAKING</span>
            </div>
          ) : isListening ? (
            <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/20 border border-cyan-400 text-cyan-200 font-mono text-[10px] shadow-[0_0_14px_rgba(0,243,255,0.4)] animate-pulse">
              <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_#00F3FF]" />
              <span className="font-bold tracking-wider">◉ LISTENING</span>
            </div>
          ) : (
            <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-[#020817]/70 border border-cyan-500/25 text-cyan-400/80 font-mono text-[10px] shadow-[inset_0_0_6px_rgba(0,243,255,0.06)]">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400/90 shadow-[0_0_6px_#00F3FF]" />
              <span className="tracking-wider">● LINK ACTIVE</span>
            </div>
          )}

          {/* Stop Voice Interruption Button */}
          {(isSpeaking || isListening) && (
            <button
              onClick={onStopSpeaking}
              title="Stop voice activity and halt speech"
              className="px-2.5 py-1 rounded bg-red-950/70 border border-red-500 text-red-300 hover:bg-red-900/80 transition text-xs font-mono flex items-center animate-pulse shadow-[0_0_12px_rgba(239,68,68,0.4)]"
            >
              <StopCircle className="w-3.5 h-3.5 mr-1" /> ■ STOP VOICE
            </button>
          )}

          {/* Vision Trigger */}
          <button
            onClick={onTriggerVision}
            title="Inspect and analyze current display"
            className="px-2.5 py-1 rounded bg-[#020817] border border-cyan-500/30 text-cyan-300 hover:border-cyan-400 hover:bg-cyan-950/40 hover:shadow-[0_0_10px_rgba(0,243,255,0.2)] transition text-xs font-mono flex items-center"
          >
            <Camera className="w-3.5 h-3.5 mr-1 text-cyan-400" /> VISION
          </button>
        </div>
      </div>

      {/* ── Message Timeline ─────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-cyan-400/40 text-xs space-y-1.5">
            <Sparkles className="w-6 h-6 text-cyan-400/60 mb-1" />
            <p className="font-display tracking-[0.2em] text-cyan-200/80">FRIDAY SECURE CHANNEL ONLINE</p>
            <p className="text-[10px] font-mono text-slate-500">Transmitting on neural stream • Speak or command to begin</p>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.role === 'user';
            const isSystem = msg.role === 'system';

            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isUser ? 'items-end' : isSystem ? 'items-center' : 'items-start'}`}
              >
                {/* Message Meta Header */}
                <div className="flex items-center space-x-2 mb-1 text-[10px] text-cyan-400/60 font-mono">
                  {isUser ? (
                    <>
                      <span className="text-slate-400">{msg.timestamp}</span>
                      <span className="font-bold text-sky-300 flex items-center">
                        <User className="w-3 h-3 mr-0.5 text-sky-400" /> USER
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="font-bold text-cyan-300 flex items-center">
                        <Bot className="w-3 h-3 mr-0.5 text-cyan-400" /> F.R.I.D.A.Y
                      </span>
                      <span className="text-slate-400">{msg.timestamp}</span>
                      {msg.mode && (
                        <span className="px-1.5 py-0.2 rounded bg-cyan-950/60 border border-cyan-500/30 text-[9px] text-cyan-200 font-mono font-bold uppercase shadow-[inset_0_0_6px_rgba(0,243,255,0.08)]">
                          {msg.mode.replace(/_/g, ' ')}
                        </span>
                      )}
                    </>
                  )}
                </div>

                {/* Holographic Message Bubble */}
                <div
                  className={`max-w-[85%] p-3 rounded-lg leading-relaxed text-xs ${
                    isUser
                      ? 'bg-[#06111f]/90 border border-sky-400/35 text-sky-100 rounded-tr-none shadow-[0_0_12px_rgba(56,189,248,0.08)]'
                      : isSystem
                      ? 'bg-slate-900/70 border border-slate-700/50 text-slate-300 text-center shadow-inner'
                      : 'bg-[#020817]/85 border border-cyan-500/25 border-l-2 border-l-cyan-400 text-slate-100 rounded-tl-none shadow-[0_0_14px_rgba(0,243,255,0.05)]'
                  }`}
                >
                  {msg.content}

                  {/* Tool execution audits attached to message */}
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-cyan-500/20 flex flex-col space-y-1">
                      {msg.toolCalls.map((tc: any, idx: number) => (
                        <div key={idx} className="flex items-center space-x-1.5 text-[10px] text-cyan-300/80">
                          <Terminal className="w-3 h-3 text-cyan-400" />
                          <span className="font-bold uppercase tracking-wider">{tc.name || tc.tool_name || 'TOOL'}:</span>
                          <span className="text-cyan-400/60 truncate">{JSON.stringify(tc.arguments || {})}</span>
                          <span className="px-1 rounded bg-cyan-500/20 text-cyan-300 text-[8px] border border-cyan-500/40">DONE</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* ── Quick Action Command Modules ─────────────────────────────────────── */}
      <div className="px-4 py-1.5 border-t border-cyan-500/15 flex space-x-2 overflow-x-auto text-[11px] font-mono text-cyan-400/80 bg-[#000205]/60">
        <button
          onClick={() => onSendMessage("What is 50 times 6?")}
          className="px-2.5 py-0.5 rounded bg-[#020817] border border-cyan-500/30 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(0,243,255,0.25)] text-cyan-300 whitespace-nowrap transition"
        >
          What is 50 times 6?
        </button>
        <button
          onClick={() => onSendMessage("What is my CPU usage?")}
          className="px-2.5 py-0.5 rounded bg-[#020817] border border-cyan-500/30 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(0,243,255,0.25)] text-cyan-300 whitespace-nowrap transition"
        >
          System CPU
        </button>
        <button
          onClick={() => onSendMessage("Open Chrome")}
          className="px-2.5 py-0.5 rounded bg-[#020817] border border-cyan-500/30 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(0,243,255,0.25)] text-cyan-300 whitespace-nowrap transition"
        >
          Open Chrome
        </button>
        <button
          onClick={() => onSendMessage("Take a screenshot")}
          className="px-2.5 py-0.5 rounded bg-[#020817] border border-cyan-500/30 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(0,243,255,0.25)] text-cyan-300 whitespace-nowrap transition"
        >
          Screenshot
        </button>
        <button
          onClick={() => onSendMessage("Remember that I prefer Python")}
          className="px-2.5 py-0.5 rounded bg-[#020817] border border-cyan-500/30 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(0,243,255,0.25)] text-cyan-300 whitespace-nowrap transition"
        >
          Remember Python
        </button>
      </div>

      {/* ── Command Input Deck ───────────────────────────────────────────────── */}
      <form
        onSubmit={handleSubmit}
        className="p-3 border-t border-cyan-500/20 bg-[#000205]/85 flex items-center space-x-2"
      >
        {/* Holographic Microphone Button */}
        <button
          type="button"
          onClick={onVoiceToggle}
          className={`px-3 py-2 rounded-lg border transition-all flex items-center font-mono text-xs ${
            isListening
              ? 'bg-cyan-500 text-black border-cyan-300 font-bold animate-pulse shadow-[0_0_16px_#00F3FF]'
              : 'bg-[#020817] text-cyan-400 border-cyan-500/30 hover:bg-cyan-950/40 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(0,243,255,0.25)]'
          }`}
          title={isListening ? 'Halt Microphone' : 'Activate Voice Listening (VAD)'}
        >
          {isListening ? (
            <>
              <Mic className="w-4 h-4 mr-1.5" />
              <span>MIC ACTIVE</span>
            </>
          ) : (
            <>
              <MicOff className="w-4 h-4 mr-1.5 text-cyan-500/70" />
              <span>MIC</span>
            </>
          )}
        </button>

        {/* Text Input Field */}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a command or speak to FRIDAY..."
          className="flex-1 bg-[#020817]/90 border border-cyan-500/30 rounded-lg px-3 py-2 text-sm text-cyan-100 placeholder-cyan-400/40 focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_12px_rgba(0,243,255,0.25)] font-mono shadow-inner transition"
        />

        {/* Multi-step Agent Planner Trigger */}
        <button
          type="button"
          onClick={handleAgentClick}
          title="Run Multi-step Cognitive Agent Planner"
          className="p-2 bg-[#020817] border border-cyan-500/40 text-cyan-300 rounded-lg hover:bg-cyan-950/50 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(0,243,255,0.2)] transition font-mono text-xs flex items-center"
        >
          <Sparkles className="w-4 h-4 mr-1 text-cyan-400" /> Agent
        </button>

        {/* Submit Button */}
        <button
          type="submit"
          className="p-2.5 bg-cyan-500/20 border border-cyan-400 text-cyan-300 rounded-lg hover:bg-cyan-500 hover:text-black hover:shadow-[0_0_14px_rgba(0,243,255,0.5)] transition duration-200"
          title="Send command"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
