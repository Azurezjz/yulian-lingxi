import type { WorkflowStep, MockWorkflowState } from './types';

const WAIT = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const MOCK_DATA: any = {
  weather: {
    summary: "根据气象工具查询，北京未来三天受冷空气影响，气温呈下降趋势。建议出行携带保暖衣物。",
    chartType: 'line',
    chartData: [
      { name: '2023-11-01', temperature: 12, humidity: 40 },
      { name: '2023-11-02', temperature: 9, humidity: 35 },
      { name: '2023-11-03', temperature: 5, humidity: 30 },
      { name: '2023-11-04', temperature: 8, humidity: 32 },
    ],
    rawData: [
      { date: '2023-11-01', weather: 'Cloudy', wind: 'North 3-4' },
      { date: '2023-11-02', weather: 'Sunny', wind: 'North 4-5' },
    ]
  },
  news: {
    summary: "为您抓取到最近 3 条 AI 相关新闻。主要集中在 OpenAI 新模型发布、欧盟 AI 法案更新以及 Google Gemini 的多模态能力升级。",
    chartType: 'none',
    chartData: [],
    rawData: [
      { title: 'OpenAI Releases GPT-5 Preview', source: 'TechCrunch', time: '2h ago' },
      { title: 'EU AI Act Finalized', source: 'Reuters', time: '5h ago' },
      { title: 'Google Integrates Gemini into Android', source: 'The Verge', time: '1d ago' },
    ]
  },
  data: {
    summary: "已根据上传的数据集完成分析。数据显示 A 类产品在 Q3 季度增长显著，占比达到 45%，建议增加该类产品的库存投入。",
    chartType: 'bar',
    chartData: [
      { name: 'Product A', sales: 4000, profit: 2400 },
      { name: 'Product B', sales: 3000, profit: 1398 },
      { name: 'Product C', sales: 2000, profit: 9800 },
      { name: 'Product D', sales: 2780, profit: 3908 },
    ],
    rawData: [
      { product: 'A', q3_growth: '+15%' },
      { product: 'B', q3_growth: '-2%' },
    ]
  }
};

export class MockAgentService {
  static async runWorkflow(
    userInput: string,
    onUpdate: (state: Partial<MockWorkflowState>) => void
  ) {
    const taskId = Date.now().toString();
    const now = () => new Date().toLocaleTimeString();

    let currentSteps: WorkflowStep[] = [
      { id: '1', name: '意图识别', description: '分析用户自然语言需求', status: 'running', timestamp: now() },
      { id: '2', name: '工具路由', description: '选择合适的工具链', status: 'pending' },
      { id: '3', name: '执行调用', description: '与外部 API 进行交互', status: 'pending' },
      { id: '4', name: '结果生成', description: '整合数据并生成可视化报告', status: 'pending' },
    ];
    
    onUpdate({ taskId, status: 'running', steps: [...currentSteps], logs: [], result: null });

    let type: 'weather' | 'news' | 'data' = 'data';
    if (userInput.includes('气温') || userInput.includes('天气')) type = 'weather';
    else if (userInput.includes('新闻') || userInput.includes('资讯')) type = 'news';

    await WAIT(1500);

    currentSteps[0].status = 'success';
    currentSteps[1].status = 'running';
    currentSteps[1].timestamp = now();
    onUpdate({ steps: [...currentSteps] });

    await WAIT(1000);

    currentSteps[1].status = 'success';
    currentSteps[2].status = 'running';
    currentSteps[2].timestamp = now();
    
    const toolName = type === 'weather' ? 'Weather API' : type === 'news' ? 'Google Search API' : 'Data Analysis Tool';
    const params = type === 'weather' ? '{"location": "Beijing", "days": 3}' : type === 'news' ? '{"query": "AI News", "limit": 3}' : '{"dataset": "sales_q3.csv"}';

    onUpdate({ 
      steps: [...currentSteps],
      logs: [{
        id: 'log-1',
        toolName: 'Orchestrator',
        inputParams: JSON.stringify({ intent: type, confidence: 0.98 }),
        status: 'success',
        duration: '120ms',
        timestamp: now()
      }]
    });

    await WAIT(2000);

    currentSteps[2].status = 'success';
    currentSteps[3].status = 'running';
    currentSteps[3].timestamp = now();

    onUpdate({
      steps: [...currentSteps],
      logs: [
        {
            id: 'log-1',
            toolName: 'Orchestrator',
            inputParams: JSON.stringify({ intent: type, confidence: 0.98 }),
            status: 'success',
            duration: '120ms',
            timestamp: now()
        },
        {
          id: 'log-2',
          toolName: toolName,
          inputParams: params,
          outputResult: '{"status": 200, "data_size": "2KB"}',
          status: 'success',
          duration: '850ms',
          timestamp: now()
        }
      ]
    });

    await WAIT(1500);

    currentSteps[3].status = 'success';
    
    onUpdate({
      status: 'success',
      steps: [...currentSteps],
      result: MOCK_DATA[type]
    });
  }
}