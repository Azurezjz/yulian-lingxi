import React from 'react';
import { CheckCircle2, Loader2, AlertCircle, Clock, Layout } from 'lucide-react';
import type { WorkflowStep } from '../../api/types';

const StepItem: React.FC<{ step: WorkflowStep; isLast: boolean }> = ({ step, isLast }) => {
  let icon;
  let colorClass;
  let bgClass;

  switch (step.status) {
    case 'success':
      icon = <CheckCircle2 size={16} />;
      colorClass = 'text-green-600';
      bgClass = 'bg-green-100';
      break;
    case 'running':
      icon = <Loader2 size={16} className="animate-spin" />;
      colorClass = 'text-blue-600';
      bgClass = 'bg-blue-100';
      break;
    case 'failed':
      icon = <AlertCircle size={16} />;
      colorClass = 'text-red-600';
      bgClass = 'bg-red-100';
      break;
    default:
      icon = <Clock size={16} />;
      colorClass = 'text-gray-400';
      bgClass = 'bg-gray-100';
  }

  return (
    <div className="relative flex gap-4 pb-8 last:pb-0">
      {!isLast && (
        <div className="absolute left-[15px] top-8 bottom-0 w-[2px] bg-gray-100" />
      )}
      <div className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center border-2 border-white shadow-sm ${bgClass} ${colorClass}`}>
        {icon}
      </div>
      <div className="flex-1 pt-1">
        <div className="flex justify-between items-center mb-1">
          <h4 className={`text-sm font-medium ${step.status === 'pending' ? 'text-gray-400' : 'text-gray-900'}`}>
            {step.name}
          </h4>
          {step.timestamp && (
            <span className="text-xs text-gray-400 font-mono">{step.timestamp}</span>
          )}
        </div>
        <p className="text-xs text-gray-500">{step.description}</p>
      </div>
    </div>
  );
};

const WorkflowOverview: React.FC<{ steps: WorkflowStep[] }> = ({ steps }) => {
  return (
    <div className="p-6">
      <h3 className="text-sm font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <Layout size={16} className="text-blue-600" />
        任务执行链路
      </h3>
      <div className="pl-2">
        {steps.map((step, index) => (
          <StepItem key={step.id} step={step} isLast={index === steps.length - 1} />
        ))}
      </div>
    </div>
  );
};

export default WorkflowOverview;