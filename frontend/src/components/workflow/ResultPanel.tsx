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

      {(() => {
        // 检查是否是多工具数据格式
        const firstItem = result.rawData && result.rawData[0];
        const isMultiToolData = firstItem && typeof firstItem === 'object' && 'type' in firstItem && 'title' in firstItem && 'data' in firstItem;
        
        if (isMultiToolData) {
          // 多工具数据：为每个工具显示图表
          return (result.rawData as Array<{type: string, title: string, data: any[], chartType?: string, chartData?: any[]}>).map((toolData, toolIdx) => {
            // 如果工具没有图表数据，跳过
            if (!toolData.chartData || toolData.chartData.length === 0 || toolData.chartType === 'none') {
              return null;
            }
            
            return (
              <div key={`chart-${toolIdx}`} className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                <h4 className="text-sm font-semibold text-gray-700 mb-4">{toolData.title} - 可视化分析</h4>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    {toolData.chartType === 'line' ? (
                      <LineChart data={toolData.chartData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis fontSize={12} tickLine={false} axisLine={false} />
                        <RechartsTooltip />
                        <Legend />
                        {/* 根据数据字段动态显示线条 */}
                        {toolData.chartData[0] && 'temperature' in toolData.chartData[0] && (
                          <Line type="monotone" dataKey="temperature" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="温度 (°C)" />
                        )}
                        {toolData.chartData[0] && 'humidity' in toolData.chartData[0] && (
                          <Line type="monotone" dataKey="humidity" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="湿度 (%)" />
                        )}
                        {toolData.chartData[0] && 'close' in toolData.chartData[0] && (
                          <Line type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="收盘价" />
                        )}
                        {toolData.chartData[0] && 'volume' in toolData.chartData[0] && (
                          <Line type="monotone" dataKey="volume" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="成交量" />
                        )}
                      </LineChart>
                    ) : (
                      <BarChart data={toolData.chartData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis fontSize={12} tickLine={false} axisLine={false} />
                        <RechartsTooltip />
                        <Legend />
                        {toolData.chartData[0] && 'sales' in toolData.chartData[0] && (
                          <Bar dataKey="sales" fill="#3B82F6" radius={[4, 4, 0, 0]} name="销售额" />
                        )}
                        {toolData.chartData[0] && 'profit' in toolData.chartData[0] && (
                          <Bar dataKey="profit" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="利润" />
                        )}
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>
            );
          });
        } else {
          // 单工具数据：显示单个图表
          if (result.chartType !== 'none' && result.chartData && result.chartData.length > 0) {
            return (
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
                        {/* 根据数据字段动态显示线条 */}
                        {result.chartData[0] && 'temperature' in result.chartData[0] && (
                          <Line type="monotone" dataKey="temperature" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="温度 (°C)" />
                        )}
                        {result.chartData[0] && 'humidity' in result.chartData[0] && (
                          <Line type="monotone" dataKey="humidity" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="湿度 (%)" />
                        )}
                        {result.chartData[0] && 'close' in result.chartData[0] && (
                          <Line type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="收盘价" />
                        )}
                        {result.chartData[0] && 'volume' in result.chartData[0] && (
                          <Line type="monotone" dataKey="volume" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="成交量" />
                        )}
                      </LineChart>
                    ) : (
                      <BarChart data={result.chartData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis fontSize={12} tickLine={false} axisLine={false} />
                        <RechartsTooltip />
                        <Legend />
                        {result.chartData[0] && 'sales' in result.chartData[0] && (
                          <Bar dataKey="sales" fill="#3B82F6" radius={[4, 4, 0, 0]} name="销售额" />
                        )}
                        {result.chartData[0] && 'profit' in result.chartData[0] && (
                          <Bar dataKey="profit" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="利润" />
                        )}
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>
            );
          }
        }
        return null;
      })()}

      {result.rawData && result.rawData.length > 0 && (() => {
        // 检查是否是多工具数据格式（包含 type 和 title）
        const firstItem = result.rawData[0];
        const isMultiToolData = firstItem && typeof firstItem === 'object' && 'type' in firstItem && 'title' in firstItem && 'data' in firstItem;
        
        if (isMultiToolData) {
          // 多工具数据：显示多个表格
          return (result.rawData as Array<{type: string, title: string, data: any[]}>).map((toolData, toolIdx) => {
            if (!toolData.data || toolData.data.length === 0) return null;
            const firstRow = toolData.data[0];
            if (!firstRow || typeof firstRow !== 'object') return null;
            
            return (
              <div key={toolIdx} className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                  <h4 className="text-sm font-semibold text-gray-700">{toolData.title}</h4>
                  <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">下载 JSON</button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 text-gray-500">
                      <tr>
                        {Object.keys(firstRow).map(key => (
                          <th key={key} className="px-4 py-2 font-medium capitalize">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {toolData.data.map((row, idx) => (
                        <tr key={idx} className="hover:bg-gray-50/50">
                          {Object.values(row).map((val: any, vIdx) => (
                            <td key={vIdx} className="px-4 py-2 text-gray-600">
                              {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          });
        } else {
          // 单工具数据：显示单个表格
          if (firstItem && typeof firstItem === 'object' && !('type' in firstItem)) {
            return (
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                  <h4 className="text-sm font-semibold text-gray-700">原始数据片段</h4>
                  <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">下载 JSON</button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 text-gray-500">
                      <tr>
                        {Object.keys(firstItem).map(key => (
                          <th key={key} className="px-4 py-2 font-medium capitalize">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {result.rawData.map((row: any, idx) => (
                        <tr key={idx} className="hover:bg-gray-50/50">
                          {Object.values(row).map((val: any, vIdx) => (
                            <td key={vIdx} className="px-4 py-2 text-gray-600">
                              {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          }
        }
        return null;
      })()}
    </div>
  );
};

export default ResultPanel;