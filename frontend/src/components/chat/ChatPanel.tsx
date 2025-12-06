import React, { useState, useRef, useEffect } from 'react';
import { Bot, Loader2, Zap, Send } from 'lucide-react';
import type { Message } from '../../api/types';
import MessageBubble from './MessageBubble';

interface ChatPanelProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ messages, isLoading, onSendMessage }) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const QUICK_PROMPTS = [
    "帮我查一下北京未来三天的气温，并画图",
    "抓取最近的国内 AI 新闻，列出 3 条并总结",
    "基于 Q3 销售数据集，生成利润分析柱状图"
  ];

  return (
    <div className="flex flex-col h-full bg-gray-50 border-r border-gray-200">
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
            <Bot size={48} className="mb-4 text-gray-300" />
            <p>我是您的 AI 助手，请下达指令</p>
          </div>
        ) : (
          messages.map(m => <MessageBubble key={m.id} message={m} />)
        )}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm ml-12 mb-4 animate-pulse">
            <Loader2 size={14} className="animate-spin" />
            <span>Agent 正在思考并调度工具...</span>
          </div>
        )}
      </div>

      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 no-scrollbar">
          {QUICK_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => setInput(prompt)}
              className="whitespace-nowrap px-3 py-1.5 bg-gray-50 hover:bg-blue-50 text-xs text-gray-600 hover:text-blue-600 border border-gray-200 hover:border-blue-200 rounded-full transition-colors flex items-center gap-1"
            >
              <Zap size={10} />
              {prompt.length > 15 ? prompt.slice(0, 15) + '...' : prompt}
            </button>
          ))}
        </div>

        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入您的指令..."
            className="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 p-3 pr-12 text-sm focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all min-h-[80px]"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`absolute bottom-3 right-3 p-2 rounded-lg transition-colors ${
              !input.trim() || isLoading
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
            }`}
          >
            <Send size={16} />
          </button>
        </div>
        <div className="text-center mt-2">
           <span className="text-[10px] text-gray-400">Powered by Lingxi LLM & ToolChain Framework</span>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;