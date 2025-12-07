# API 接口规范文档

本文档定义了前后端交互的 API 接口规范，**后端开发人员必须严格按照此规范实现接口**，确保与前端无缝对接。

## 一、基础信息

### 接口基础路径
- **开发环境**：`http://localhost:8000/api`
- **生产环境**：根据部署情况配置

### 数据格式
- **请求格式**：`application/json`
- **响应格式**：`application/json`
- **字符编码**：`UTF-8`

### 通用响应结构

所有 API 响应遵循以下统一格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**状态码说明：**
- `200`：成功
- `400`：请求参数错误
- `500`：服务器内部错误
- `503`：服务暂时不可用（如工具 API 调用失败）

---

## 二、核心接口

### 1. 工作流执行接口

**接口路径**：`POST /api/workflow/execute`

**功能描述**：接收用户自然语言输入，执行意图识别、工具调度、结果生成等完整流程。

**请求参数：**

```json
{
  "userInput": "查广州近7天最高气温",
  "conversationId": "optional_conversation_id"
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `userInput` | string | 是 | 用户输入的自然语言需求 |
| `conversationId` | string | 否 | 对话 ID，用于多轮对话上下文 |

**响应数据：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "1704067200000",
    "status": "success",
    "steps": [
      {
        "id": "1",
        "name": "意图识别",
        "description": "分析用户自然语言需求",
        "status": "success",
        "timestamp": "10:30:15"
      },
      {
        "id": "2",
        "name": "工具路由",
        "description": "选择合适的工具链",
        "status": "success",
        "timestamp": "10:30:16"
      },
      {
        "id": "3",
        "name": "执行调用",
        "description": "与外部 API 进行交互",
        "status": "success",
        "timestamp": "10:30:18"
      },
      {
        "id": "4",
        "name": "结果生成",
        "description": "整合数据并生成可视化报告",
        "status": "success",
        "timestamp": "10:30:20"
      }
    ],
    "logs": [
      {
        "id": "log-1",
        "toolName": "Weather API",
        "inputParams": "{\"location\": \"Guangzhou\", \"days\": 7}",
        "outputResult": "{\"status\": 200, \"data_size\": \"2KB\"}",
        "status": "success",
        "duration": "850ms",
        "timestamp": "10:30:18"
      }
    ],
    "result": {
      "summary": "根据气象工具查询，广州未来7天最高气温呈波动趋势，最高温度出现在第3天，达到28°C。",
      "chartType": "line",
      "chartData": [
        { "name": "2024-01-01", "temperature": 25, "humidity": 65 },
        { "name": "2024-01-02", "temperature": 27, "humidity": 70 },
        { "name": "2024-01-03", "temperature": 28, "humidity": 68 }
      ],
      "rawData": [
        { "date": "2024-01-01", "weather": "Sunny", "wind": "South 2-3", "maxTemp": 25, "minTemp": 18 }
      ]
    }
  }
}
```

**字段说明：**

#### `steps` 数组（工作流步骤）
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 步骤唯一标识 |
| `name` | string | 步骤名称（如 "意图识别"、"工具路由"） |
| `description` | string | 步骤描述 |
| `status` | string | 状态：`pending` / `running` / `success` / `failed` |
| `timestamp` | string | 时间戳（格式：`HH:mm:ss`） |

#### `logs` 数组（工具调用日志）
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 日志唯一标识 |
| `toolName` | string | 工具名称（如 "Weather API"、"News API"） |
| `inputParams` | string | 输入参数（JSON 字符串） |
| `outputResult` | string | 输出结果（JSON 字符串，可选） |
| `status` | string | 状态：`success` / `failed` |
| `duration` | string | 执行时长（如 "850ms"） |
| `timestamp` | string | 时间戳（格式：`HH:mm:ss`） |

#### `result` 对象（执行结果）
| 字段 | 类型 | 说明 |
|------|------|------|
| `summary` | string | 结果摘要文本 |
| `chartType` | string | 图表类型：`line` / `bar` / `none` |
| `chartData` | array | 图表数据数组（格式见下方） |
| `rawData` | array | 原始数据数组（可选） |

**图表数据格式：**
```json
{
  "chartData": [
    { "name": "2024-01-01", "temperature": 25, "humidity": 65 },
    { "name": "2024-01-02", "temperature": 27, "humidity": 70 }
  ]
}
```
- `name` 字段为 X 轴标签（必填）
- 其他字段为数据系列（如 `temperature`、`humidity`）

---

### 2. 流式响应接口（可选，用于实时更新）

**接口路径**：`POST /api/workflow/execute/stream`

**功能描述**：支持 Server-Sent Events (SSE) 流式返回，实时更新工作流状态。

**请求参数：** 同 `/api/workflow/execute`

**响应格式：** SSE 流式数据

```
data: {"type": "step_update", "data": {"stepId": "1", "status": "running"}}

data: {"type": "log_add", "data": {"id": "log-1", "toolName": "Weather API", ...}}

data: {"type": "complete", "data": {"result": {...}}}
```

**事件类型：**
- `step_update`：步骤状态更新
- `log_add`：新增工具调用日志
- `complete`：工作流执行完成

---

### 3. 工具状态查询接口

**接口路径**：`GET /api/tools/status`

**功能描述**：查询所有工具的可用状态。

**响应数据：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "tools": [
      {
        "name": "Weather API",
        "status": "available",
        "description": "天气查询工具，支持7天预报"
      },
      {
        "name": "News API",
        "status": "available",
        "description": "新闻检索工具"
      },
      {
        "name": "Stock API",
        "status": "unavailable",
        "description": "股票数据查询工具（API 配额已用完）"
      }
    ]
  }
}
```

---

## 三、错误处理

### 错误响应格式

```json
{
  "code": 400,
  "message": "参数错误：userInput 不能为空",
  "data": null
}
```

### 常见错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `400` | 请求参数错误 | `userInput` 为空 |
| `500` | 服务器内部错误 | 模型调用失败、工具执行异常 |
| `503` | 服务暂时不可用 | 外部 API 调用失败、工具不可用 |

---

## 四、数据格式约定

### 1. 时间格式
- **时间戳**：`HH:mm:ss`（如 `10:30:15`）
- **日期**：`YYYY-MM-DD`（如 `2024-01-01`）

### 2. JSON 字符串字段
- `inputParams`、`outputResult` 等字段为 JSON 字符串，需要在前端解析

### 3. 图表数据
- `chartData` 数组中的对象必须包含 `name` 字段作为 X 轴标签
- 其他字段作为数据系列，支持多个系列（如 `temperature`、`humidity`）

---

## 五、前后端对接检查清单

### 后端开发人员
- [ ] 接口路径与本文档一致
- [ ] 响应格式完全符合规范（包括字段名、类型）
- [ ] 错误处理返回统一格式
- [ ] `steps`、`logs`、`result` 字段结构正确
- [ ] `chartData` 格式符合前端图表组件要求

### 前端开发人员
- [ ] 使用 `types.ts` 中定义的类型
- [ ] API 调用使用统一的错误处理
- [ ] 正确解析 `inputParams`、`outputResult` 等 JSON 字符串字段
- [ ] 图表组件正确渲染 `chartData`

### 协同人员
- [ ] 配置 Vite 代理，解决跨域问题
- [ ] 测试完整流程：输入 → 后端处理 → 前端展示
- [ ] 验证错误场景处理

---

## 六、示例代码

### 后端示例（FastAPI）

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WorkflowRequest(BaseModel):
    userInput: str
    conversationId: str | None = None

@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest):
    # 1. 意图识别
    # 2. 工具调度
    # 3. 结果生成
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "taskId": "...",
            "status": "success",
            "steps": [...],
            "logs": [...],
            "result": {...}
        }
    }
```

### 前端示例（TypeScript）

```typescript
import type { WorkflowResult } from './api/types';

async function executeWorkflow(userInput: string) {
  const response = await fetch('http://localhost:8000/api/workflow/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userInput })
  });
  
  const result = await response.json();
  if (result.code === 200) {
    return result.data;
  } else {
    throw new Error(result.message);
  }
}
```

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：前后端协同人员


