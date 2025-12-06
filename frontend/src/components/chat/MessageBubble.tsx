import React from 'react';
import { User, Bot } from 'lucide-react';
import type { Message } from '../../api/types';

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-blue-100 text-blue-600' : 'bg-purple-100 text-purple-600'}`}>
          {isUser ? <User size={18} /> : <Bot size={18} />}
        </div>
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-400">{message.timestamp}</span>
            {!isUser && message.relatedTool && (
              <span className="text-[10px] px-1.5 py-0.5 bg-purple-50 text-purple-600 border border-purple-100 rounded-full">
                调用: {message.relatedTool}
              </span>
            )}
          </div>
          <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
            isUser 
              ? 'bg-blue-600 text-white rounded-tr-none' 
              : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
          }`}>
            {message.content}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;