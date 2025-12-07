# 项目测试指南

本文档提供完整的项目测试步骤，包括前端测试、后端测试和前后端联调测试。

---

## 一、测试前准备

### 1. 环境检查

确保已安装以下环境：

**前端环境：**
- Node.js >= 18
- npm 或 yarn

**后端环境：**
- Python >= 3.9
- pip

### 2. 依赖安装

**前端依赖：**
```bash
cd frontend
npm install
```

**后端依赖：**
```bash
cd backend
# 创建虚拟环境（推荐）
conda create -n lingxi_backend python=3.9 -y
conda activate lingxi_backend
# 或使用 venv
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

---

## 二、前端测试（使用 Mock 数据）

### 1. 启动前端服务

```bash
cd frontend
npm run dev
```

访问：http://localhost:5173

### 2. 功能测试清单

#### ✅ 基础界面测试
- [ ] 页面正常加载，无白屏
- [ ] 左侧聊天面板显示欢迎消息
- [ ] 右侧工作流面板显示"在左侧发起对话以开始任务"提示

#### ✅ 聊天功能测试
- [ ] 输入框可以正常输入文字
- [ ] 点击发送按钮或按 Enter 键可以发送消息
- [ ] 用户消息显示在聊天面板中
- [ ] 系统回复消息正常显示

#### ✅ 工作流展示测试
测试场景 1：天气查询
```
输入："查北京天气"
预期：
- 右侧"任务总览"标签页显示 4 个步骤（意图识别→工具路由→执行调用→结果生成）
- 步骤状态依次变为 running → success
- "工具日志"标签页显示工具调用记录
- "执行结果"标签页显示天气数据和折线图
```

测试场景 2：新闻检索
```
输入："查最近的 AI 新闻"
预期：
- 工作流正常执行
- 结果显示新闻列表（卡片形式）
```

测试场景 3：数据分析
```
输入："分析销售数据"
预期：
- 工作流正常执行
- 结果显示柱状图
```

#### ✅ UI 交互测试
- [ ] 切换标签页（任务总览、工具日志、执行结果、工具状态）正常
- [ ] 图表正常渲染（折线图、柱状图）
- [ ] 加载状态正常显示
- [ ] 响应式布局正常（调整浏览器窗口大小）

### 3. 浏览器控制台检查

打开浏览器开发者工具（F12），检查：
- [ ] 无 JavaScript 错误（Console 标签页）
- [ ] 无网络请求错误（Network 标签页）
- [ ] 无 React 警告

---

## 三、后端测试（API 接口测试）

### 1. 启动后端服务

```bash
cd backend
# 激活虚拟环境
conda activate lingxi_backend
# 或
venv\Scripts\activate  # Windows

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 2. 使用 Swagger UI 测试

访问 http://localhost:8000/docs，在 Swagger UI 中测试：

#### 测试 1：健康检查
```
GET /health
预期响应：
{
  "status": "ok"
}
```

#### 测试 2：根路径
```
GET /
预期响应：
{
  "message": "语联灵犀 API 服务",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### 测试 3：工具状态查询
```
GET /api/tools/status
预期响应：
{
  "code": 200,
  "message": "success",
  "data": {
    "tools": [...]
  }
}
```

#### 测试 4：工作流执行（当前返回 Mock 数据）
```
POST /api/workflow/execute
请求体：
{
  "userInput": "查北京天气",
  "conversationId": null
}

预期响应：
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "...",
    "status": "success",
    "steps": [],
    "logs": [],
    "result": {...}
  }
}
```

### 3. 使用 curl 测试（命令行）

**Windows PowerShell：**
```powershell
# 健康检查
curl http://localhost:8000/health

# 工作流执行
curl -X POST "http://localhost:8000/api/workflow/execute" `
  -H "Content-Type: application/json" `
  -d '{\"userInput\": \"查北京天气\"}'
```

**Linux/Mac：**
```bash
# 健康检查
curl http://localhost:8000/health

# 工作流执行
curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "查北京天气"}'
```

### 4. 使用 Python 脚本测试

创建测试脚本 `backend/test_api.py`：

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/health")
    print("健康检查:", response.json())
    assert response.status_code == 200

def test_workflow():
    """测试工作流执行"""
    response = requests.post(
        f"{BASE_URL}/api/workflow/execute",
        json={"userInput": "查北京天气"}
    )
    print("工作流执行:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    assert response.status_code == 200
    assert response.json()["code"] == 200

if __name__ == "__main__":
    test_health()
    test_workflow()
    print("✅ 所有测试通过")
```

运行测试：
```bash
cd backend
python test_api.py
```

---

## 四、前后端联调测试

### 1. 同时启动前后端

**终端 1 - 启动后端：**
```bash
cd backend
conda activate lingxi_backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 2. 配置前端连接后端

当前前端使用 Mock 数据。要连接真实后端，需要修改 `frontend/src/api/mockWorkflow.ts` 或创建新的 API 服务文件。

**创建真实 API 服务文件** `frontend/src/api/workflow.ts`：

```typescript
import type { WorkflowStep, MockWorkflowState } from './types';

const API_BASE_URL = '/api';  // 使用 Vite 代理

export class WorkflowService {
  static async executeWorkflow(
    userInput: string,
    conversationId?: string
  ): Promise<MockWorkflowState> {
    const response = await fetch(`${API_BASE_URL}/workflow/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userInput,
        conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API 请求失败: ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.code !== 200) {
      throw new Error(result.message || '工作流执行失败');
    }

    return result.data;
  }

  static async getToolsStatus() {
    const response = await fetch(`${API_BASE_URL}/tools/status`);
    const result = await response.json();
    return result.data;
  }
}
```

**修改** `frontend/src/layouts/MainLayout.tsx`，替换 Mock 服务：

```typescript
// 将
import { MockAgentService } from '../api/mockWorkflow';

// 改为
import { WorkflowService } from '../api/workflow';
```

### 3. 测试前后端通信

#### ✅ 跨域测试
- [ ] 前端能正常发送请求到后端
- [ ] 浏览器控制台无 CORS 错误
- [ ] 网络请求状态码为 200

#### ✅ 数据格式测试
- [ ] 后端返回的数据格式符合前端 `types.ts` 定义
- [ ] 前端能正确解析后端响应
- [ ] 工作流步骤正常显示
- [ ] 工具日志正常显示
- [ ] 结果数据正常展示

#### ✅ 错误处理测试
- [ ] 后端返回错误时，前端有错误提示
- [ ] 网络断开时，前端有错误提示
- [ ] 后端超时时，前端有超时提示

---

## 五、端到端测试场景

### 场景 1：单工具调用 - 天气查询

**步骤：**
1. 前端输入："查北京近7天天气"
2. 前端发送请求到后端
3. 后端识别意图，调用天气工具
4. 后端返回结果
5. 前端展示天气数据和折线图

**验证点：**
- [ ] 意图识别正确（识别为天气查询）
- [ ] 工具调用成功
- [ ] 数据格式正确
- [ ] 图表正常渲染

### 场景 2：多工具联动 - 股票分析

**步骤：**
1. 前端输入："查贵州茅台近5日收盘价，计算涨幅，生成趋势图"
2. 后端依次调用：股票工具 → 计算工具 → 绘图工具
3. 前端展示最终结果

**验证点：**
- [ ] 多工具串联执行
- [ ] 工具间数据传递正确
- [ ] 最终结果整合正确

### 场景 3：错误处理

**步骤：**
1. 前端输入无效请求
2. 后端返回错误
3. 前端显示错误提示

**验证点：**
- [ ] 错误信息清晰
- [ ] 用户界面友好
- [ ] 系统不崩溃

---

## 六、性能测试

### 1. 响应时间测试

使用浏览器开发者工具的 Network 标签页：
- [ ] API 请求响应时间 < 3 秒（正常情况）
- [ ] 页面加载时间 < 2 秒
- [ ] 图表渲染时间 < 1 秒

### 2. 并发测试

使用工具（如 Apache Bench 或 Postman）测试并发请求：

```bash
# 使用 ab 工具（需要安装 Apache）
ab -n 100 -c 10 http://localhost:8000/health
```

---

## 七、常见问题排查

### 问题 1：前端无法连接后端

**可能原因：**
- 后端服务未启动
- 端口被占用
- CORS 配置错误

**解决方法：**
1. 检查后端服务是否运行：访问 http://localhost:8000/health
2. 检查端口占用：`netstat -ano | findstr :8000` (Windows)
3. 检查 `backend/app/main.py` 中的 CORS 配置

### 问题 2：后端返回数据格式错误

**可能原因：**
- 字段名不匹配
- 数据类型错误
- 缺少必需字段

**解决方法：**
1. 对比 `docs/API_SPEC.md` 中的规范
2. 检查后端返回的数据结构
3. 使用 Swagger UI 查看实际返回数据

### 问题 3：图表不显示

**可能原因：**
- 数据格式不正确
- Recharts 组件配置错误
- 数据为空

**解决方法：**
1. 检查 `chartData` 格式（必须包含 `name` 字段）
2. 检查浏览器控制台错误
3. 验证数据是否为空

---

## 八、测试检查清单

### 前端测试
- [ ] 页面正常加载
- [ ] 聊天功能正常
- [ ] 工作流展示正常
- [ ] 图表渲染正常
- [ ] 无控制台错误

### 后端测试
- [ ] API 接口正常响应
- [ ] 数据格式符合规范
- [ ] 错误处理正常
- [ ] CORS 配置正确

### 前后端联调
- [ ] 前后端通信正常
- [ ] 数据传递正确
- [ ] 错误处理完善
- [ ] 性能满足要求

### 端到端测试
- [ ] 单工具调用场景通过
- [ ] 多工具联动场景通过
- [ ] 错误场景处理正常

---

## 九、测试报告模板

测试完成后，填写以下信息：

```
测试日期：____
测试人员：____

前端测试：
- 状态：✅ 通过 / ❌ 失败
- 问题：____

后端测试：
- 状态：✅ 通过 / ❌ 失败
- 问题：____

前后端联调：
- 状态：✅ 通过 / ❌ 失败
- 问题：____

总体评价：
____
```

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：测试负责人


