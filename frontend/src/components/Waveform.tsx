import React from 'react';
import type { AssistantState } from './AIReactor';

interface WaveformProps {
  state: AssistantState;
}

export const Waveform: React.FC<WaveformProps> = ({ state }) => {
  const bars = Array.from({ length: 28 });
  const isActive = state === 'LISTENING' || state === 'SPEAKING' || state === 'THINKING' || state === 'EXECUTING';

  return (
    <div className="flex items-center justify-center space-x-1 h-8 py-1 select-none">
      {bars.map((_, i) => {
        const height = isActive 
          ? Math.sin(i * 0.45 + Date.now() * 0.006) * 12 + 14 
          : 4;
        
        return (
          <div
            key={i}
            className="w-1 rounded-full transition-all duration-150"
            style={{
              height: `${height}px`,
              background: state === 'LISTENING' 
                ? '#f59e0b' 
                : state === 'SPEAKING'
                ? '#f97316'
                : state === 'THINKING'
                ? '#fbbf24'
                : state === 'EXECUTING'
                ? '#eab308'
                : 'rgba(245, 158, 11, 0.25)',
              boxShadow: isActive ? '0 0 6px rgba(245, 158, 11, 0.6)' : 'none'
            }}
          />
        );
      })}
    </div>
  );
};
