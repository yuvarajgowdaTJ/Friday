import React from 'react';
import { Cpu, HardDrive, Wifi, Battery, Server } from 'lucide-react';

export interface SystemStatsData {
  status: string;
  os: string;
  cpu: { percent: number; cores: number };
  ram: { percent: number; used_gb: number; total_gb: number };
  disk: { percent: number; free_gb: number; total_gb: number };
  battery?: { percent: number; power_plugged: boolean };
  network: { online: boolean; hostname: string };
}

interface SystemStatsProps {
  stats: SystemStatsData | null;
}

export const SystemStats: React.FC<SystemStatsProps> = ({ stats }) => {
  if (!stats) {
    return (
      <div className="jarvis-card p-4 font-mono text-xs text-cyan-400/60 animate-pulse">
        CONNECTING TO SYSTEM DIAGNOSTICS...
      </div>
    );
  }

  return (
    <div className="jarvis-card p-4 flex flex-col justify-between space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2">
        <div className="flex items-center space-x-2">
          <Server className="w-4 h-4 text-cyan-400" />
          <span className="font-display text-xs tracking-wider text-cyan-200 uppercase">SYSTEM DIAGNOSTICS</span>
        </div>
        <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          {stats.status}
        </span>
      </div>

      {/* Grid Meters */}
      <div className="grid grid-cols-2 gap-3 font-mono text-xs">
        {/* CPU */}
        <div className="bg-slate-900/60 p-2.5 rounded border border-cyan-500/10">
          <div className="flex justify-between items-center mb-1">
            <span className="flex items-center text-slate-400">
              <Cpu className="w-3.5 h-3.5 mr-1 text-cyan-400" /> CPU
            </span>
            <span className="text-cyan-300 font-bold">{stats.cpu.percent}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full transition-all duration-300"
              style={{ width: `${stats.cpu.percent}%` }}
            />
          </div>
          <div className="mt-1 text-[10px] text-slate-500">{stats.cpu.cores} CORES ACTIVE</div>
        </div>

        {/* RAM */}
        <div className="bg-slate-900/60 p-2.5 rounded border border-cyan-500/10">
          <div className="flex justify-between items-center mb-1">
            <span className="flex items-center text-slate-400">
              <Server className="w-3.5 h-3.5 mr-1 text-purple-400" /> RAM
            </span>
            <span className="text-purple-300 font-bold">{stats.ram.percent}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full transition-all duration-300"
              style={{ width: `${stats.ram.percent}%` }}
            />
          </div>
          <div className="mt-1 text-[10px] text-slate-500">{stats.ram.used_gb} / {stats.ram.total_gb} GB</div>
        </div>

        {/* DISK */}
        <div className="bg-slate-900/60 p-2.5 rounded border border-cyan-500/10">
          <div className="flex justify-between items-center mb-1">
            <span className="flex items-center text-slate-400">
              <HardDrive className="w-3.5 h-3.5 mr-1 text-amber-400" /> DISK
            </span>
            <span className="text-amber-300 font-bold">{stats.disk.percent}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-gradient-to-r from-amber-500 to-orange-500 h-full transition-all duration-300"
              style={{ width: `${stats.disk.percent}%` }}
            />
          </div>
          <div className="mt-1 text-[10px] text-slate-500">{stats.disk.free_gb} GB FREE</div>
        </div>

        {/* NETWORK / BATTERY */}
        <div className="bg-slate-900/60 p-2.5 rounded border border-cyan-500/10 flex flex-col justify-between">
          <div className="flex justify-between items-center">
            <span className="flex items-center text-slate-400">
              <Wifi className="w-3.5 h-3.5 mr-1 text-emerald-400" /> NET
            </span>
            <span className={`font-bold ${stats.network.online ? 'text-emerald-400' : 'text-red-400'}`}>
              {stats.network.online ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
          {stats.battery && (
            <div className="flex justify-between items-center mt-1 pt-1 border-t border-slate-800">
              <span className="flex items-center text-slate-400 text-[10px]">
                <Battery className="w-3 h-3 mr-1 text-cyan-400" /> BAT
              </span>
              <span className="text-cyan-300 font-bold text-[10px]">{stats.battery.percent}%</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer OS string */}
      <div className="font-mono text-[10px] text-slate-500 truncate text-center pt-1 border-t border-cyan-500/10">
        HOST: {stats.network.hostname} | OS: {stats.os}
      </div>
    </div>
  );
};
