import React from 'react';
import { Terminal, ShieldAlert, Play, Search, Calculator, Globe, Camera, HardDrive } from 'lucide-react';
import type { ToolLog } from './ToolActivity';

interface ActivityLogPanelProps {
  logs: ToolLog[];
  pendingConfirmation?: ToolLog | null;
  onConfirmTool?: (log: ToolLog) => void;
  onRejectTool?: (log: ToolLog) => void;
}

export const ActivityLogPanel: React.FC<ActivityLogPanelProps> = ({
  logs,
  pendingConfirmation,
  onConfirmTool,
  onRejectTool,
}) => {
  const getToolIcon = (toolName: string) => {
    const name = toolName.toLowerCase();
    if (name.includes('search') || name.includes('duckduckgo') || name.includes('research')) return Search;
    if (name.includes('calc') || name.includes('math')) return Calculator;
    if (name.includes('browser') || name.includes('web') || name.includes('open_browser')) return Globe;
    if (name.includes('screenshot') || name.includes('vision') || name.includes('screen')) return Camera;
    if (name.includes('file') || name.includes('disk')) return HardDrive;
    return Terminal;
  };

  return (
    <div className="hud-panel flex flex-col h-full relative select-none font-mono text-xs">
      {/* ── Panel Header ──────────────────────────────────────────────────────── */}
      <div className="p-3 border-b border-cyan-500/20 flex items-center justify-between bg-[#000205]/60">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <div>
            <h3 className="font-display text-xs tracking-[0.2em] text-cyan-100 uppercase glow-text-cyan leading-none">
              ACTIVITY / TOOL INTELLIGENCE
            </h3>
            <span className="font-mono text-[8px] tracking-wider text-cyan-400/60 uppercase">
              LIVE DIRECTIVE AUDIT STREAM
            </span>
          </div>
        </div>
        <span className="text-[10px] text-cyan-400/80 flex items-center px-2 py-0.5 rounded bg-cyan-950/40 border border-cyan-500/30">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 inline-block mr-1.5 animate-pulse shadow-[0_0_6px_#00F3FF]" />
          ACTIVE
        </span>
      </div>

      {/* ── Confirmation Modal Overlay for Privileged Directives ──────────────── */}
      {pendingConfirmation && (
        <div className="absolute inset-0 bg-[#000205]/95 backdrop-blur-md z-30 p-4 flex flex-col justify-center items-center text-center space-y-3 border border-cyan-500/40 rounded-lg">
          <div className="w-12 h-12 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center text-cyan-300 animate-bounce shadow-[0_0_15px_rgba(0,243,255,0.4)]">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-display text-xs text-cyan-100 tracking-wider uppercase glow-text-cyan">
              AUTHORIZATION REQUIRED
            </h4>
            <p className="text-[11px] text-cyan-200/80 mt-1">
              FRIDAY requests permission to execute directive:
            </p>
            <div className="mt-2 p-2.5 bg-[#020817] border border-cyan-500/40 rounded text-cyan-200 text-xs font-bold shadow-[inset_0_0_10px_rgba(0,243,255,0.08)]">
              {pendingConfirmation.tool_name}({JSON.stringify(pendingConfirmation.arguments || {})})
            </div>
          </div>
          <div className="flex space-x-2 pt-1">
            <button
              onClick={() => onConfirmTool?.(pendingConfirmation)}
              className="px-4 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs rounded transition flex items-center shadow-[0_0_12px_rgba(0,243,255,0.4)]"
            >
              <Play className="w-3.5 h-3.5 mr-1" /> Approve
            </button>
            <button
              onClick={() => onRejectTool?.(pendingConfirmation)}
              className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs rounded border border-slate-700 transition"
            >
              Deny
            </button>
          </div>
        </div>
      )}

      {/* ── Directive Audit Log Feed ─────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {logs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-cyan-400/40 text-[11px] space-y-1">
            <Terminal className="w-6 h-6 opacity-40 mb-1 text-cyan-400" />
            <p className="tracking-wider">NO DIRECTIVE ACTIVITY REGISTERED</p>
            <p className="text-[9px] text-slate-500">Subsystem executions will stream here</p>
          </div>
        ) : (
          logs.map((log) => {
            const ToolIcon = getToolIcon(log.tool_name);
            const isSuccess = log.status === 'SUCCESS' || log.status === 'SAFE';
            const isWarning = log.status === 'CONFIRMATION_REQUIRED';

            return (
              <div
                key={log.id}
                className="p-2.5 bg-[#020817]/80 border border-cyan-500/20 rounded-lg flex flex-col space-y-1 hover:border-cyan-400/45 transition duration-150 shadow-[inset_0_0_8px_rgba(0,243,255,0.02)]"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1.5 font-bold text-cyan-100">
                    <ToolIcon className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{log.tool_name}</span>
                  </div>
                  <span className="text-[10px] text-cyan-400/60">{log.timestamp}</span>
                </div>

                <div className="text-[11px] text-cyan-200/80 truncate">
                  {log.details || 'Subsystem directive executed'}
                </div>

                <div className="flex items-center justify-between text-[10px] pt-1 border-t border-cyan-500/15">
                  <span className="text-slate-400 truncate max-w-[60%]">
                    {log.arguments ? JSON.stringify(log.arguments) : 'DEFAULT'}
                  </span>
                  <span
                    className={`px-1.5 py-0.2 rounded font-bold uppercase text-[9px] ${
                      isSuccess
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : isWarning
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 animate-pulse'
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}
                  >
                    {log.status}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
