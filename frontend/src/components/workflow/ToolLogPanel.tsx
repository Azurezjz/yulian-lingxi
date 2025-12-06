import React from 'react';
import { Terminal } from 'lucide-react';
import type { ToolCallLog } from '../../api/types';

const ToolLogPanel: React.FC<{ logs: ToolCallLog[] }> = ({ logs }) => {
  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-400">
        <Terminal size={32} className="mb-2 opacity-50" />
        <p className="text-sm">暂无工具调用记录</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="space-y-3">
        {logs.map((log) => (
          <div key={log.id} className="border border-gray-200 rounded-lg bg-white overflow-hidden shadow-sm transition-shadow hover:shadow-md">
            <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                <span className="font-medium text-sm text-gray-700">{log.toolName}</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span className="font-mono">{log.duration}</span>
                <span>{log.timestamp}</span>
              </div>
            </div>
            <div className="p-3 bg-slate-900 overflow-x-auto">
              <div className="text-xs font-mono text-green-400 mb-1 opacity-70"># Input Parameters</div>
              <pre className="text-xs font-mono text-gray-300 mb-2">{log.inputParams}</pre>
              {log.outputResult && (
                <>
                  <div className="border-t border-slate-700 my-2"></div>
                  <div className="text-xs font-mono text-blue-400 mb-1 opacity-70"># Output Result</div>
                  <pre className="text-xs font-mono text-gray-300">{log.outputResult}</pre>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ToolLogPanel;