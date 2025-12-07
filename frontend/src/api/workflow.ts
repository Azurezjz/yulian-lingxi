/**
 * 真实后端 API 服务
 * 替换 Mock 数据，连接真实后端
 */
import type { MockWorkflowState } from './types';

const API_BASE_URL = '/api';  // 使用 Vite 代理，实际请求会被转发到 http://localhost:8000/api

export interface WorkflowExecuteRequest {
  userInput: string;
  conversationId?: string | null;
}

export interface WorkflowExecuteResponse {
  code: number;
  message: string;
  data: MockWorkflowState;
}

export interface ApiError {
  code: number;
  message: string;
  detail?: string;
}

export class WorkflowService {
  /**
   * 执行工作流
   * @param userInput 用户输入的自然语言
   * @param conversationId 对话 ID（可选）
   * @param onUpdate 状态更新回调（用于流式更新）
   */
  static async executeWorkflow(
    userInput: string,
    conversationId?: string | null,
    onUpdate?: (state: Partial<MockWorkflowState>) => void
  ): Promise<MockWorkflowState> {
    try {
      // 先更新初始状态
      if (onUpdate) {
        onUpdate({
          status: 'running',
          steps: [],
          logs: [],
          result: null
        });
      }

      const response = await fetch(`${API_BASE_URL}/workflow/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userInput,
          conversationId: conversationId || null,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API 请求失败: ${response.status} ${errorText}`);
      }

      const result: WorkflowExecuteResponse = await response.json();

      if (result.code !== 200) {
        throw new Error(result.message || '工作流执行失败');
      }

      // 更新最终状态
      if (onUpdate) {
        onUpdate(result.data);
      }

      return result.data;
    } catch (error) {
      console.error('工作流执行错误:', error);
      
      // 更新错误状态
      if (onUpdate) {
        onUpdate({
          status: 'failed',
        });
      }

      throw error;
    }
  }

  /**
   * 查询工具状态
   */
  static async getToolsStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/tools/status`);

      if (!response.ok) {
        throw new Error(`API 请求失败: ${response.status}`);
      }

      const result = await response.json();

      if (result.code !== 200) {
        throw new Error(result.message || '查询工具状态失败');
      }

      return result.data;
    } catch (error) {
      console.error('查询工具状态错误:', error);
      throw error;
    }
  }
}


