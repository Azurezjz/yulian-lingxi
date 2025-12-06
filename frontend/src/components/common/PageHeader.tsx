import React from 'react';
import { Zap } from 'lucide-react';

const PageHeader: React.FC = () => {
  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between shadow-sm flex-shrink-0 z-10">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
          <Zap size={20} fill="currentColor" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-gray-900 leading-tight">语联灵犀</h1>
          <p className="text-xs text-gray-500">异构工具联动系统 v1.0.0-beta</p>
        </div>
      </div>
    </header>
  );
};

export default PageHeader;