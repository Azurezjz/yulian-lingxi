import React from 'react';
import { Terminal } from 'lucide-react';

const TOOLS = [
  { name: 'Weather API', desc: '全球气象数据实时查询接口', status: 'active', category: '生活' },
  { name: 'Google Search', desc: '联网实时搜索与资讯抓取', status: 'active', category: '资讯' },
  { name: 'Data Analysis', desc: 'Pandas/Python 数据处理沙箱', status: 'active', category: '计算' },
  { name: 'Image Gen', desc: 'DALL-E 3 图像生成模型', status: 'maintenance', category: '创作' },
];

const ToolStatusPanel: React.FC = () => {
  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {TOOLS.map((tool, idx) => (
          <div key={idx} className="p-4 border border-gray-200 rounded-xl hover:border-blue-300 transition-colors bg-white group">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-gray-100 rounded-md group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                  <Terminal size={16} />
                </div>
                <span className="font-semibold text-gray-800">{tool.name}</span>
              </div>
              <span className={`px-2 py-0.5 text-[10px] rounded-full border ${
                tool.status === 'active' 
                  ? 'bg-green-50 text-green-600 border-green-100' 
                  : 'bg-yellow-50 text-yellow-600 border-yellow-100'
              }`}>
                {tool.status === 'active' ? '在线' : '维护中'}
              </span>
            </div>
            <p className="text-xs text-gray-500 mb-3 line-clamp-2">{tool.desc}</p>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gray-400 bg-gray-50 px-2 py-0.5 rounded">{tool.category}</span>
              <span className="text-[10px] text-gray-400">v2.1.0</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ToolStatusPanel;