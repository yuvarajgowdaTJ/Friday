import React from 'react';
import { Terminal, AlertTriangle, Play } from 'lucide-react';

export interface ToolLog {
  id: string;
  tool_name: string;
  status: 'SAFE' | 'CONFIRMATION_REQUIRED' | 'SUCCESS' | 'ERROR' | 'BLOCKED';
  timestamp: string;
  details?: string;
  arguments?: any;
}

interface ToolActivityProps {
  logs: ToolLog[];
  pendingConfirmation?: ToolLog | null;
  onConfirmTool?: (log: ToolLog) => void;
  onRejectTool?: (log: ToolLog) => void;
}

export const ToolActivity: React.FC<ToolActivityProps> = ({
  logs,
  pendingConfirmation,
  onConfirmTool,
  onRejectTool
}) => {
  return (
    <div className="jarvis-card flex flex-col h-full relative">
      {/* Header */}
      <div className="p-3 border-b border-cyan-500/20 flex items-center justify-between bg-slate-900/40">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="font-display text-xs tracking-wider text-cyan-200">TOOL EXECUTION LOG</span>
        </div>
        <span className="font-mono text-[10px] text-slate-400">
          SECURITY ENGINE ACTIVE
        </span>
      </div>

      {/* Confirmation Modal overlay if tool execution needs permission */}
      {pendingConfirmation && (
        <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-md z-20 p-4 flex flex-col justify-center items-center text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-amber-500/20 border border-amber-400 flex items-center justify-center text-amber-400 animate-bounce">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-display text-sm text-amber-300 tracking-wider">USER CONFIRMATION REQUIRED</h4>
            <p className="font-mono text-xs text-slate-300 mt-1 max-w-xs">
              FRIDAY requests permission to execute tool:
            </p>
            <div className="mt-2 p-2 bg-slate-900 border border-amber-500/30 rounded font-mono text-xs text-cyan-300">
              {pendingConfirmation.tool_name}({JSON.stringify(pendingConfirmation.arguments || {})})
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => onConfirmTool?.(pendingConfirmation)}
              className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs rounded shadow transition flex items-center"
            >
              <Play className="w-3.5 h-3.5 mr-1" /> Approve Execution
            </button>
            <button
              onClick={() => onRejectTool?.(pendingConfirmation)}
              className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs rounded border border-slate-600 transition"
            >
              Deny
            </button>
          </div>
        </div>
      )}

      {/* Log list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-xs">
        {logs.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-[11px]">
            No tool executions logged yet.
          </div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className="p-2 bg-slate-900/60 border border-cyan-500/10 rounded flex flex-col space-y-1"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-cyan-300">{log.tool_name}</span>
                <span className="text-[10px] text-slate-500">{log.timestamp}</span>
              </div>
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-slate-400 truncate max-w-[70%]">
                  {log.details || 'Executing system function'}
                </span>
                <span
                  className={`px-1.5 py-0.2 rounded font-bold ${
                    log.status === 'SUCCESS' || log.status === 'SAFE'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : log.status === 'CONFIRMATION_REQUIRED'
                      ? 'bg-amber-500/20 text-amber-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {log.status}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
