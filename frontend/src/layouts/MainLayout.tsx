import React, { useState } from 'react';
import { Layout, Terminal, FileText, Zap, PlayCircle } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import ChatPanel from '../components/chat/ChatPanel';
import WorkflowOverview from '../components/workflow/WorkflowOverview';
import ToolLogPanel from '../components/workflow/ToolLogPanel';
import ResultPanel from '../components/workflow/ResultPanel';
import ToolStatusPanel from '../components/workflow/ToolStatusPanel';
import type { Message, MockWorkflowState } from '../api/types';
import { MockAgentService } from '../api/mockWorkflow';

const MainLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [messages, setMessages] = useState<Message[]>([
    { id: '0', role: 'agent', content: '你好，我是语联灵犀 AI 助手。我可以帮你查询天气、检索新闻或进行简单的数据分析。请告诉我你的需求。', timestamp: '10:00:00' }
  ]);
  const [loading, setLoading] = useState(false);
  
  const [workflowState, setWorkflowState] = useState<MockWorkflowState>({
    taskId: '',
    status: 'idle',
    steps: [],
    logs: [],
    result: null
  });

  const handleSendMessage = async (text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    setActiveTab('overview');
    setWorkflowState(prev => ({ ...prev, status: 'running', steps: [], logs: [], result: null }));

    await MockAgentService.runWorkflow(text, (updatedState) => {
      setWorkflowState(prev => ({ ...prev, ...updatedState }));
    });

    setMessages(prev => [...prev, {
      id: (Date.now() + 1).toString(),
      role: 'agent',
      content: '任务已完成，请在右侧面板查看详细执行报告和结果。',
      timestamp: new Date().toLocaleTimeString(),
      relatedTool: 'Workflow Engine'
    }]);
    
    setActiveTab('result');
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 text-gray-900 font-sans">
      <PageHeader />
      
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[400px] flex-shrink-0 border-r border-gray-200 bg-white h-full shadow-[4px_0_24px_rgba(0,0,0,0.02)] z-10">
          <ChatPanel 
            messages={messages} 
            isLoading={loading} 
            onSendMessage={handleSendMessage} 
          />
        </div>

        <div className="flex-1 flex flex-col bg-gray-50/50 min-w-0">
          <div className="h-12 border-b border-gray-200 bg-white flex items-center px-4 gap-6">
            <button 
              onClick={() => setActiveTab('overview')}
              className={`h-full flex items-center gap-2 text-sm font-medium border-b-2 transition-colors px-1 ${
                activeTab === 'overview' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Layout size={16} />
              任务总览
            </button>
            <button 
              onClick={() => setActiveTab('logs')}
              className={`h-full flex items-center gap-2 text-sm font-medium border-b-2 transition-colors px-1 ${
                activeTab === 'logs' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Terminal size={16} />
              工具日志
              {workflowState.logs.length > 0 && <span className="bg-gray-100 text-gray-600 px-1.5 rounded-full text-[10px]">{workflowState.logs.length}</span>}
            </button>
            <button 
              onClick={() => setActiveTab('result')}
              className={`h-full flex items-center gap-2 text-sm font-medium border-b-2 transition-colors px-1 ${
                activeTab === 'result' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <FileText size={16} />
              执行结果
              {workflowState.result && <span className="w-2 h-2 rounded-full bg-green-500" />}
            </button>
            <button 
              onClick={() => setActiveTab('status')}
              className={`h-full flex items-center gap-2 text-sm font-medium border-b-2 transition-colors px-1 ${
                activeTab === 'status' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Zap size={16} />
              工具状态
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <div className="max-w-5xl mx-auto h-full">
              {activeTab === 'overview' && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-[400px]">
                  {workflowState.steps.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-gray-400 pt-20">
                       <PlayCircle size={48} className="mb-4 text-gray-200" />
                       <p>在左侧发起对话以开始任务</p>
                    </div>
                  ) : (
                    <WorkflowOverview steps={workflowState.steps} />
                  )}
                </div>
              )}
              
              {activeTab === 'logs' && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-[400px]">
                  <ToolLogPanel logs={workflowState.logs} />
                </div>
              )}
              
              {activeTab === 'result' && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-[400px]">
                  <ResultPanel result={workflowState.result} />
                </div>
              )}
              
              {activeTab === 'status' && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-[400px]">
                  <ToolStatusPanel />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MainLayout;