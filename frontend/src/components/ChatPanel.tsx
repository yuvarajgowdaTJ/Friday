
import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Camera, Bot, Sparkles, StopCircle } from 'lucide-react';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  mode?: string;
  toolCalls?: any[];
}

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (msg: string) => void;
  onVoiceToggle: () => void;
  onStopSpeaking: () => void;
  isListening: boolean;
  isSpeaking: boolean;
  onTriggerVision: () => void;
  onTriggerAgent: (query: string) => void;
  voiceError?: string | null;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onSendMessage,
  onVoiceToggle,
  onStopSpeaking,
  isListening,
  isSpeaking,
  onTriggerVision,
  onTriggerAgent,
  voiceError,
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
    <div className="jarvis-card flex flex-col h-full">
      {/* Panel Header */}
      <div className="p-3 border-b border-cyan-500/20 flex justify-between items-center bg-slate-900/40">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-cyan-400" />
          <span className="font-display text-xs tracking-wider text-cyan-200">CONVERSATION FEED</span>
        </div>
        <div className="flex space-x-2">
          {/* Stop Speaking button — visible only when FRIDAY is speaking or listening */}
          {(isSpeaking || isListening) && (
            <button
              onClick={onStopSpeaking}
              title="Stop FRIDAY"
              className="p-1.5 rounded bg-red-500/20 border border-red-500/40 text-red-300 hover:bg-red-500/30 transition text-xs flex items-center animate-pulse"
            >
              <StopCircle className="w-3.5 h-3.5 mr-1" /> Stop
            </button>
          )}
          <button
            onClick={onTriggerVision}
            title="Look at screen (Vision Analysis)"
            className="p-1.5 rounded bg-purple-500/20 border border-purple-500/30 text-purple-300 hover:bg-purple-500/30 transition text-xs flex items-center"
          >
            <Camera className="w-3.5 h-3.5 mr-1" /> Vision
          </button>
        </div>
      </div>

      {/* Voice error notice */}
      {voiceError && (
        <div className="mx-3 mt-2 px-2 py-1.5 rounded bg-red-900/30 border border-red-500/30 text-red-300 font-mono text-[10px]">
          ⚠ {voiceError}
        </div>
      )}

      {/* Message Timeline */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-sm">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs">
            <Sparkles className="w-8 h-8 mb-2 opacity-40 text-cyan-400" />
            <p>FRIDAY ready. Speak or type a command.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className="flex items-center space-x-2 mb-1 text-[10px] text-slate-500">
                <span className="font-bold text-cyan-400">{msg.role === 'user' ? 'USER' : 'FRIDAY'}</span>
                <span>{msg.timestamp}</span>
                {msg.mode && (
                  <span className="px-1.5 py-0.2 bg-slate-800 rounded text-[9px] text-purple-400">{msg.mode}</span>
                )}
              </div>
              <div className={`max-w-[85%] p-3 rounded-lg leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-cyan-950/60 border border-cyan-500/30 text-cyan-100 rounded-tr-none'
                  : 'bg-slate-900/80 border border-purple-500/20 text-slate-200 rounded-tl-none'
              }`}>
                {msg.content}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Action Chips */}
      <div className="px-3 py-1.5 border-t border-cyan-500/10 flex space-x-2 overflow-x-auto text-[11px] font-mono text-cyan-400/80">
        <button onClick={() => onSendMessage("What's my CPU usage?")} className="px-2 py-0.5 rounded bg-slate-900 border border-cyan-500/20 hover:border-cyan-400 whitespace-nowrap">System CPU</button>
        <button onClick={() => onSendMessage("Open Chrome")} className="px-2 py-0.5 rounded bg-slate-900 border border-cyan-500/20 hover:border-cyan-400 whitespace-nowrap">Open Chrome</button>
        <button onClick={() => onSendMessage("Remember that I prefer Python")} className="px-2 py-0.5 rounded bg-slate-900 border border-cyan-500/20 hover:border-cyan-400 whitespace-nowrap">Remember Python</button>
        <button onClick={() => onSendMessage("Take a screenshot")} className="px-2 py-0.5 rounded bg-slate-900 border border-cyan-500/20 hover:border-cyan-400 whitespace-nowrap">Screenshot</button>
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-cyan-500/20 bg-slate-900/60 flex items-center space-x-2">
        {/* Mic toggle */}
        <button
          type="button"
          onClick={onVoiceToggle}
          className={`p-2.5 rounded-lg border transition-all ${
            isListening
              ? 'bg-cyan-500 text-slate-950 border-cyan-400 animate-pulse shadow-[0_0_12px_#00f3ff]'
              : 'bg-slate-800 text-cyan-400 border-cyan-500/30 hover:bg-slate-700'
          }`}
          title={isListening ? 'Stop listening' : 'Start microphone (backend VAD)'}
        >
          {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Command FRIDAY or ask a question..."
          className="flex-1 bg-slate-950/80 border border-cyan-500/30 rounded-lg px-3 py-2 text-sm text-cyan-100 placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono"
        />

        <button
          type="button"
          onClick={handleAgentClick}
          title="Run Multi-step Agent Planner"
          className="p-2 bg-purple-600/30 border border-purple-500/40 text-purple-300 rounded-lg hover:bg-purple-600/50 transition font-mono text-xs flex items-center"
        >
          <Sparkles className="w-4 h-4 mr-1 text-purple-400" /> Agent
        </button>

        <button
          type="submit"
          className="p-2.5 bg-cyan-500/20 border border-cyan-400 text-cyan-300 rounded-lg hover:bg-cyan-500/40 transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
