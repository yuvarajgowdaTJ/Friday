import React from 'react';
import { Activity, ShieldAlert, Cpu, Zap, Mic, Volume2 } from 'lucide-react';

export type AssistantState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'EXECUTING' | 'ERROR';

interface AIReactorProps {
  state: AssistantState;
  statusText?: string;
  wakeDetected?: boolean;
}

export const AIReactor: React.FC<AIReactorProps> = ({ state, statusText, wakeDetected }) => {
  const getStateColor = () => {
    switch (state) {
      case 'LISTENING':
        return '#00f3ff'; // Bright cyan
      case 'THINKING':
        return '#a855f7'; // Neon purple
      case 'SPEAKING':
        return '#3b82f6'; // Bright blue
      case 'EXECUTING':
        return '#f59e0b'; // Amber yellow
      case 'ERROR':
        return '#ef4444'; // Red
      default:
        return '#00f3ff';
    }
  };

  const color = getStateColor();

  return (
    <div className="flex flex-col items-center justify-center p-6 text-center select-none">
      {/* Reactor Outer Ring Container */}
      <div className="relative w-64 h-64 flex items-center justify-center">
        {/* Outer Rotating Ring with Dashes */}
        <div 
          className="absolute inset-0 rounded-full border-2 border-dashed animate-spin-slow opacity-60"
          style={{ borderColor: color }}
        />

        {/* Inner Counter-Rotating Ring */}
        <div 
          className="absolute inset-4 rounded-full border border-dotted animate-spin-reverse opacity-40"
          style={{ borderColor: color }}
        />

        {/* Glowing Reactor Core */}
        <div 
          className="reactor-core w-40 h-40 rounded-full flex flex-col items-center justify-center relative transition-all duration-500"
          style={{
            background: `radial-gradient(circle, ${color}33 0%, rgba(13,18,30,0.9) 70%)`,
            border: `2px solid ${color}`,
            boxShadow: `0 0 35px ${color}66, inset 0 0 25px ${color}66`
          }}
        >
          {/* Status Icon */}
          <div className="mb-2">
            {state === 'LISTENING' && <Mic className="w-8 h-8 animate-bounce text-cyan-400" />}
            {state === 'THINKING' && <Cpu className="w-8 h-8 animate-pulse text-purple-400" />}
            {state === 'SPEAKING' && <Volume2 className="w-8 h-8 animate-pulse text-blue-400" />}
            {state === 'EXECUTING' && <Zap className="w-8 h-8 animate-spin text-amber-400" />}
            {state === 'ERROR' && <ShieldAlert className="w-8 h-8 text-red-500" />}
            {state === 'IDLE' && <Activity className="w-8 h-8 opacity-80 text-cyan-400" />}
          </div>

          {/* Core Title */}
          <span className="font-display text-lg font-bold tracking-widest text-white">
            FRIDAY
          </span>
          <span className="font-mono text-xs tracking-wider opacity-80 uppercase mt-0.5" style={{ color }}>
            {state}
          </span>
        </div>

        {/* Orbiting Satellite Nodes */}
        <div className="absolute w-full h-full animate-spin-slow pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-cyan-400 shadow-[0_0_10px_#00f3ff]" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-purple-500 shadow-[0_0_10px_#a855f7]" />
        </div>
      </div>

      {/* Dynamic Status Text */}
      <div className="mt-4">
        <p className="font-mono text-sm tracking-wide text-cyan-300">
          {statusText || (state === 'IDLE' ? 'SYSTEMS OPERATIONAL — AWAITING INPUT' : state)}
        </p>
        {wakeDetected && (
          <span className="inline-block mt-2 px-3 py-1 bg-cyan-500/20 border border-cyan-400 text-cyan-300 font-mono text-xs rounded-full animate-pulse">
            WAKE WORD DETECTED: "HEY FRIDAY"
          </span>
        )}
      </div>
    </div>
  );
};
