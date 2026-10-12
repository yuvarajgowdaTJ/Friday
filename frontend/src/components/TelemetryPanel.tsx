import React from 'react';
import { Cpu, Server, HardDrive, Thermometer, Wifi, Activity } from 'lucide-react';
import type { SystemStatsData } from './SystemStats';

interface TelemetryPanelProps {
  stats: SystemStatsData | null;
}

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({ stats }) => {
  if (!stats) {
    return (
      <div className="hud-panel p-4 flex flex-col justify-center items-center h-full text-center space-y-2 font-mono text-xs text-cyan-400/60 select-none">
        <Activity className="w-5 h-5 text-cyan-400 animate-spin-slow" />
        <span className="tracking-widest">ACQUIRING HARDWARE TELEMETRY...</span>
      </div>
    );
  }

  // Estimated synthetic thermal reading based on CPU load
  const estimatedTemp = Math.round(38 + (stats.cpu.percent * 0.42));

  return (
    <div className="hud-panel p-3.5 flex flex-col justify-between h-full space-y-3 font-mono text-xs select-none">
      {/* ── Header: Title & Diagnostic Indicator ────────────────────────────── */}
      <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <div>
            <h3 className="font-display text-xs tracking-[0.2em] text-cyan-100 uppercase glow-text-cyan leading-none">
              SYSTEM INTELLIGENCE
            </h3>
            <span className="font-mono text-[8px] tracking-wider text-cyan-400/60 uppercase">
              LIVE HARDWARE TELEMETRY
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-cyan-950/40 text-cyan-300 border border-cyan-500/30 text-[10px] shadow-[inset_0_0_6px_rgba(0,243,255,0.1)]">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          <span>SYS {stats.status}</span>
        </div>
      </div>

      {/* ── Metric 1: CPU Utilization Meter ──────────────────────────────────── */}
      <div className="bg-[#020817]/80 p-2.5 rounded-lg border border-cyan-500/20 flex flex-col space-y-1.5 shadow-[inset_0_0_10px_rgba(0,243,255,0.03)]">
        <div className="flex justify-between items-center text-[11px]">
          <span className="flex items-center text-cyan-100 font-bold">
            <Cpu className="w-3.5 h-3.5 mr-1.5 text-cyan-400" /> CPU COGNITION
          </span>
          <span className="text-cyan-200 font-display font-bold text-sm tracking-wider glow-text-cyan">
            {stats.cpu.percent}%
          </span>
        </div>

        {/* Segmented Energy Bar */}
        <div className="relative w-full bg-[#000205] h-2 rounded-full overflow-hidden border border-cyan-500/30">
          <div
            className="bg-gradient-to-r from-blue-600 via-sky-400 to-cyan-300 h-full transition-all duration-300 shadow-[0_0_10px_#00F3FF]"
            style={{ width: `${stats.cpu.percent}%` }}
          />
        </div>

        <div className="flex justify-between text-[10px] text-cyan-400/70 pt-0.5">
          <span>CORES: {stats.cpu.cores} ACTIVE</span>
          <span className={stats.cpu.percent > 75 ? 'text-cyan-200 font-bold' : 'text-cyan-400/70'}>
            LOAD: {stats.cpu.percent > 75 ? 'SURGE' : 'NOMINAL'}
          </span>
        </div>
      </div>

      {/* ── Metric 2: RAM Memory Meter ───────────────────────────────────────── */}
      <div className="bg-[#020817]/80 p-2.5 rounded-lg border border-cyan-500/20 flex flex-col space-y-1.5 shadow-[inset_0_0_10px_rgba(0,243,255,0.03)]">
        <div className="flex justify-between items-center text-[11px]">
          <span className="flex items-center text-cyan-100 font-bold">
            <Server className="w-3.5 h-3.5 mr-1.5 text-sky-400" /> SYSTEM MEMORY
          </span>
          <span className="text-sky-200 font-display font-bold text-sm tracking-wider glow-text-cyan">
            {stats.ram.percent}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full bg-[#000205] h-2 rounded-full overflow-hidden border border-cyan-500/30">
          <div
            className="bg-gradient-to-r from-cyan-600 via-sky-400 to-cyan-200 h-full transition-all duration-300 shadow-[0_0_8px_#38BDF8]"
            style={{ width: `${stats.ram.percent}%` }}
          />
        </div>

        <div className="flex justify-between text-[10px] text-cyan-400/70 pt-0.5">
          <span>USED: {stats.ram.used_gb} GB</span>
          <span>TOTAL: {stats.ram.total_gb} GB</span>
        </div>
      </div>

      {/* ── Metric 3: Storage / Disk Capacity ────────────────────────────────── */}
      <div className="bg-[#020817]/80 p-2.5 rounded-lg border border-cyan-500/20 flex flex-col space-y-1.5 shadow-[inset_0_0_10px_rgba(0,243,255,0.03)]">
        <div className="flex justify-between items-center text-[11px]">
          <span className="flex items-center text-cyan-100 font-bold">
            <HardDrive className="w-3.5 h-3.5 mr-1.5 text-cyan-400" /> STORAGE MATRIX
          </span>
          <span className="text-cyan-200 font-display font-bold text-sm tracking-wider glow-text-cyan">
            {stats.disk.percent}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full bg-[#000205] h-2 rounded-full overflow-hidden border border-cyan-500/30">
          <div
            className="bg-gradient-to-r from-blue-700 via-cyan-500 to-sky-300 h-full transition-all duration-300"
            style={{ width: `${stats.disk.percent}%` }}
          />
        </div>

        <div className="flex justify-between text-[10px] text-cyan-400/70 pt-0.5">
          <span>FREE: {stats.disk.free_gb} GB</span>
          <span>TOTAL: {stats.disk.total_gb} GB</span>
        </div>
      </div>

      {/* ── Metric 4 & 5: Thermal Sensor & Network Telemetry ─────────────────── */}
      <div className="grid grid-cols-2 gap-2">
        {/* Thermal Sensor Module */}
        <div className="bg-[#020817]/80 p-2 rounded-lg border border-cyan-500/20 flex flex-col justify-between shadow-[inset_0_0_8px_rgba(0,243,255,0.03)]">
          <div className="flex items-center text-[10px] text-cyan-300 font-bold">
            <Thermometer className="w-3 h-3 mr-1 text-cyan-400" /> THERMAL
          </div>
          <div className="mt-1 flex items-baseline justify-between">
            <span className="text-base font-display font-bold text-cyan-100 glow-text-cyan">{estimatedTemp}°C</span>
            <span className="text-[9px] text-emerald-400 font-mono tracking-wider">NOMINAL</span>
          </div>
        </div>

        {/* Network Telemetry Module */}
        <div className="bg-[#020817]/80 p-2 rounded-lg border border-cyan-500/20 flex flex-col justify-between shadow-[inset_0_0_8px_rgba(0,243,255,0.03)]">
          <div className="flex items-center text-[10px] text-cyan-300 font-bold">
            <Wifi className="w-3 h-3 mr-1 text-cyan-400" /> NETWORK
          </div>
          <div className="mt-1 flex items-baseline justify-between">
            <span className="text-xs font-bold text-cyan-200 uppercase truncate">
              {stats.network.online ? 'LINKED' : 'OFFLINE'}
            </span>
            <span className="text-[9px] text-cyan-400/60 font-mono">1.2ms</span>
          </div>
        </div>
      </div>

      {/* ── Host Specs Footer ────────────────────────────────────────────────── */}
      <div className="pt-2 border-t border-cyan-500/15 text-[9px] text-cyan-400/60 truncate text-center">
        NODE: {stats.network.hostname} | OS: {stats.os}
      </div>
    </div>
  );
};
