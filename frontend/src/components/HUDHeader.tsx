import React, { useState, useEffect } from 'react';
import { ShieldCheck, Volume2, VolumeX, Settings as SettingsIcon, Brain, Wifi, WifiOff } from 'lucide-react';
import type { AssistantState } from './AIReactor';

interface HUDHeaderProps {
  assistantState: AssistantState;
  soundEnabled: boolean;
  onToggleSound: () => void;
  onOpenSettings: () => void;
  onToggleMemory: () => void;
  safeMode: boolean;
  voiceContinuous: boolean;
  voiceError?: string | null;
  networkOnline?: boolean;
}

export const HUDHeader: React.FC<HUDHeaderProps> = ({
  assistantState,
  soundEnabled,
  onToggleSound,
  onOpenSettings,
  onToggleMemory,
  safeMode,
  voiceContinuous,
  voiceError,
  networkOnline = true,
}) => {
  const [timeStr, setTimeStr] = useState('');
  const [dateStr, setDateStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }));
      setDateStr(now.toLocaleDateString('en-US', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase());
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const getStateBadgeColor = () => {
    switch (assistantState) {
      case 'LISTENING':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-400 shadow-[0_0_8px_rgba(0,243,255,0.3)] animate-pulse';
      case 'THINKING':
        return 'bg-sky-500/20 text-sky-200 border-sky-400 shadow-[0_0_8px_rgba(56,189,248,0.3)]';
      case 'SPEAKING':
        return 'bg-blue-500/20 text-blue-200 border-blue-400 shadow-[0_0_8px_rgba(14,165,233,0.3)]';
      case 'EXECUTING':
        return 'bg-cyan-600/20 text-cyan-200 border-cyan-500 shadow-[0_0_8px_rgba(0,243,255,0.3)]';
      case 'ERROR':
        return 'bg-red-950/60 text-red-300 border-red-500/70 shadow-[0_0_8px_rgba(239,68,68,0.3)]';
      case 'IDLE':
      default:
        return 'bg-cyan-950/40 text-cyan-300/90 border-cyan-500/30';
    }
  };

  return (
    <header className="h-16 px-5 border-b border-cyan-500/20 bg-[#000205]/90 backdrop-blur-xl flex items-center justify-between z-30 select-none relative">
      {/* Bottom Subtle Holographic Laser Hairline */}
      <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent pointer-events-none" />

      {/* TOP LEFT: Holographic Beacon, Brand Identity, Diagnostics */}
      <div className="flex items-center space-x-3.5">
        {/* Core Beacon Pulse */}
        <div className="relative flex items-center justify-center w-4 h-4">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_10px_#00F3FF]" />
          <div className="absolute w-4 h-4 rounded-full border border-cyan-400/60 animate-ping" />
        </div>

        <div>
          <div className="flex items-baseline space-x-2">
            <h1 className="font-display font-black text-lg tracking-[0.28em] text-cyan-100 glow-text-cyan leading-none">
              F.R.I.D.A.Y
            </h1>
            <span className="font-mono text-[9px] text-cyan-400/80 px-1 py-0.2 rounded border border-cyan-500/30 bg-cyan-950/40 tracking-wider">
              v5.0
            </span>
          </div>
          <div className="flex items-center space-x-2 text-[9px] font-mono tracking-wider text-cyan-300/70 uppercase mt-0.5">
            <span className="tracking-[0.16em]">FUTURE READY INTELLIGENT DIGITAL ASSISTANT</span>
            <span className="text-cyan-500/40">•</span>
            <span className="text-slate-400">STATUS:</span>
            <span className={`px-2 py-0.2 rounded border font-bold ${getStateBadgeColor()}`}>
              {assistantState}
            </span>
          </div>
        </div>

        {/* Subsystem Mode Badges */}
        <div className="hidden lg:flex items-center space-x-2 pl-4 border-l border-cyan-500/20">
          <div className="px-2.5 py-1 rounded bg-[#020817]/80 border border-cyan-500/30 text-cyan-200 font-mono text-[10px] flex items-center shadow-[inset_0_0_8px_rgba(0,243,255,0.06)]">
            <ShieldCheck className="w-3.5 h-3.5 mr-1.5 text-cyan-400" />
            <span>SECURITY:</span>
            <span className="ml-1 text-cyan-300 font-bold">{safeMode ? 'SAFE' : 'OVERRIDE'}</span>
          </div>
          <div className="px-2.5 py-1 rounded bg-[#020817]/80 border border-cyan-500/30 text-cyan-200 font-mono text-[10px] flex items-center shadow-[inset_0_0_8px_rgba(0,243,255,0.06)]">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mr-1.5 animate-pulse shadow-[0_0_6px_#00F3FF]" />
            <span>VOICE LOOP:</span>
            <span className="ml-1 text-cyan-300 font-bold">{voiceContinuous ? 'CONTINUOUS' : 'MANUAL'}</span>
          </div>
        </div>
      </div>

      {/* Center Voice Error Warning if present */}
      {voiceError && (
        <div className="hidden md:flex items-center px-3 py-1 rounded bg-red-950/60 border border-red-500/50 text-red-300 font-mono text-[11px] truncate max-w-sm shadow-[0_0_12px_rgba(239,68,68,0.25)]">
          <span className="mr-1 text-red-400 font-bold">⚠</span> {voiceError}
        </div>
      )}

      {/* TOP RIGHT: Clock & Date, Network Link, Holographic Controls */}
      <div className="flex items-center space-x-4">
        {/* Clock & Date Module */}
        <div className="flex flex-col items-end font-mono">
          <div className="flex items-center space-x-1.5">
            <span className="text-[8px] text-cyan-400/60 uppercase tracking-widest font-mono">SYSTEM TIME</span>
            <span className="text-base font-display font-bold text-cyan-100 tracking-wider glow-text-cyan">
              {timeStr || '--:--:--'}
            </span>
          </div>
          <div className="text-[9px] text-cyan-300/60 tracking-widest">
            {dateStr || 'SYSTEM CLOCK'}
          </div>
        </div>

        {/* Network Connectivity Badge */}
        <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#020817]/80 border border-cyan-500/30 font-mono text-[10px] shadow-[inset_0_0_8px_rgba(0,243,255,0.06)]">
          {networkOnline ? (
            <>
              <Wifi className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-cyan-400 font-bold">LINK ONLINE</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5 text-red-400" />
              <span className="text-red-400 font-bold">LINK OFFLINE</span>
            </>
          )}
        </div>

        {/* Action Controls: Small Holographic Command Modules */}
        <div className="flex items-center space-x-1.5 pl-3 border-l border-cyan-500/20">
          <button
            onClick={onToggleMemory}
            className="p-2 rounded bg-[#020817]/80 border border-cyan-500/30 text-cyan-400 hover:text-cyan-100 hover:border-cyan-400 hover:bg-cyan-950/40 hover:shadow-[0_0_12px_rgba(0,243,255,0.25)] transition duration-200"
            title="Toggle Memory Archive"
          >
            <Brain className="w-4 h-4" />
          </button>

          <button
            onClick={onToggleSound}
            className="p-2 rounded bg-[#020817]/80 border border-cyan-500/30 text-cyan-400 hover:text-cyan-100 hover:border-cyan-400 hover:bg-cyan-950/40 hover:shadow-[0_0_12px_rgba(0,243,255,0.25)] transition duration-200"
            title={soundEnabled ? 'Mute Speech Output' : 'Unmute Speech Output'}
          >
            {soundEnabled ? (
              <Volume2 className="w-4 h-4 text-cyan-400" />
            ) : (
              <VolumeX className="w-4 h-4 text-slate-500" />
            )}
          </button>

          <button
            onClick={onOpenSettings}
            className="p-2 rounded bg-[#020817]/80 border border-cyan-500/30 text-cyan-400 hover:text-cyan-100 hover:border-cyan-400 hover:bg-cyan-950/40 hover:shadow-[0_0_12px_rgba(0,243,255,0.25)] transition duration-200"
            title="System Settings"
          >
            <SettingsIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
