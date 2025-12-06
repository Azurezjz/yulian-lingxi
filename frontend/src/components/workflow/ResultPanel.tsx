import React from 'react';
import { BarChart3, Bot } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import type { WorkflowResult } from '../../api/types';

const ResultPanel: React.FC<{ result: WorkflowResult | null }> = ({ result }) => {
  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-400">
        <BarChart3 size={32} className="mb-2 opacity-50" />
        <p className="text-sm">等待任务执行完成...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-100">
        <h4 className="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <Bot size={16} />
          Agent 总结
        </h4>
        <p className="text-sm text-blue-800 leading-relaxed">
          {result.summary}
        </p>
      </div>

      {result.chartType !== 'none' && result.chartData && (
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <h4 className="text-sm font-semibold text-gray-700 mb-4">可视化分析</h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              {result.chartType === 'line' ? (
                <LineChart data={result.chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis fontSize={12} tickLine={false} axisLine={false} />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="temperature" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="温度 (°C)" />
                  {result.chartData[0].humidity && <Line type="monotone" dataKey="humidity" stroke="#10B981" strokeWidth={2} name="湿度 (%)" />}
                </LineChart>
              ) : (
                <BarChart data={result.chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis fontSize={12} tickLine={false} axisLine={false} />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="sales" fill="#3B82F6" radius={[4, 4, 0, 0]} name="销售额" />
                  <Bar dataKey="profit" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="利润" />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {result.rawData && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h4 className="text-sm font-semibold text-gray-700">原始数据片段</h4>
            <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">下载 JSON</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  {Object.keys(result.rawData[0]).map(key => (
                    <th key={key} className="px-4 py-2 font-medium capitalize">{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {result.rawData.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50/50">
                    {Object.values(row).map((val: any, vIdx) => (
                      <td key={vIdx} className="px-4 py-2 text-gray-600">{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultPanel;