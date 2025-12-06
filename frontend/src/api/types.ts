export type TaskStatus = 'idle' | 'running' | 'success' | 'failed';
export type StepStatus = 'pending' | 'running' | 'success' | 'failed';

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  status: StepStatus;
  timestamp?: string;
}

export interface ToolCallLog {
  id: string;
  toolName: string;
  inputParams: string;
  outputResult?: string;
  status: 'success' | 'failed';
  duration: string;
  timestamp: string;
}

export interface ChartData {
  name: string;
  [key: string]: string | number;
}

export interface WorkflowResult {
  summary: string;
  chartType?: 'line' | 'bar' | 'none';
  chartData?: ChartData[];
  rawData?: Record<string, any>[];
}

export interface Message {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  relatedTool?: string;
}
// ===================

export interface MockWorkflowState {
  taskId: string;
  status: TaskStatus;
  steps: WorkflowStep[];
  logs: ToolCallLog[];
  result: WorkflowResult | null;
}