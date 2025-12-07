# 连接真实后端指南

本文档说明如何将前端从 Mock 数据切换到真实后端 API。

---

## ✅ 已完成的更改

### 1. 前端更改

**创建真实 API 服务：**
- ✅ `frontend/src/api/workflow.ts` - 真实后端 API 服务
- ✅ 更新 `frontend/src/layouts/MainLayout.tsx` - 使用真实 API 替代 Mock

**主要改动：**
- 将 `MockAgentService` 替换为 `WorkflowService`
- 添加错误处理机制
- 支持状态更新回调

### 2. 后端更改

**更新 API 路由：**
- ✅ `backend/app/api/routes.py` - 返回完整的数据结构
- ✅ 根据用户输入判断意图类型
- ✅ 返回符合前端期望的数据格式

---

## 🚀 测试步骤

### 第一步：启动后端服务

```bash
cd backend

# 激活虚拟环境
conda activate lingxi_backend
# 或
venv\Scripts\activate  # Windows

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端启动：**
- 访问 http://localhost:8000/docs 应该能看到 Swagger UI
- 访问 http://localhost:8000/health 应该返回 `{"status": "ok"}`

### 第二步：启动前端服务

```bash
cd frontend
npm run dev
```

**验证前端启动：**
- 访问 http://localhost:5173 应该能看到界面

### 第三步：测试连接

1. **打开浏览器开发者工具（F12）**
   - 切换到 "Network" 标签页
   - 确保能看到网络请求

2. **在前端界面输入测试消息：**
   - 输入："查北京天气"
   - 点击发送

3. **检查网络请求：**
   - 应该能看到 `POST /api/workflow/execute` 请求
   - 状态码应该是 200
   - 响应应该包含完整的工作流数据

4. **验证界面显示：**
   - ✅ 右侧"任务总览"应该显示 4 个步骤
   - ✅ "工具日志"应该显示工具调用记录
   - ✅ "执行结果"应该显示天气数据和折线图

---

## 🔍 测试场景

### 场景 1：天气查询

**输入：** "查北京天气" 或 "查广州近7天天气"

**预期结果：**
- 意图识别为天气查询
- 显示折线图（气温趋势）
- 显示原始天气数据

### 场景 2：新闻检索

**输入：** "查最近的 AI 新闻" 或 "检索科技资讯"

**预期结果：**
- 意图识别为新闻检索
- 显示新闻列表（卡片形式）
- 无图表（chartType: "none"）

### 场景 3：数据分析

**输入：** "分析销售数据" 或 "查看产品统计"

**预期结果：**
- 意图识别为数据分析
- 显示柱状图
- 显示分析结果摘要

---

## 🐛 常见问题排查

### 问题 1：前端无法连接后端

**症状：** 浏览器控制台显示 `Failed to fetch` 或 `Network Error`

**解决方法：**
1. 确认后端服务已启动（访问 http://localhost:8000/health）
2. 检查 `frontend/vite.config.ts` 中的代理配置：
   ```typescript
   server: {
     proxy: {
       '/api': {
         target: 'http://localhost:8000',
         changeOrigin: true,
       }
     }
   }
   ```
3. 重启前端服务（`npm run dev`）

### 问题 2：CORS 错误

**症状：** 浏览器控制台显示 `CORS policy` 错误

**解决方法：**
1. 检查 `backend/app/main.py` 中的 CORS 配置：
   ```python
   allow_origins=["http://localhost:5173", "http://localhost:3000"]
   ```
2. 确保前端地址在允许列表中
3. 重启后端服务

### 问题 3：数据格式不匹配

**症状：** 前端显示异常或白屏

**解决方法：**
1. 检查浏览器控制台的错误信息
2. 对比后端返回的数据格式和 `frontend/src/api/types.ts` 中的类型定义
3. 确保后端返回的数据包含所有必需字段：
   - `taskId`
   - `status`
   - `steps`（数组）
   - `logs`（数组）
   - `result`（对象，包含 `summary`、`chartType`、`chartData`）

### 问题 4：图表不显示

**症状：** 工作流执行成功，但图表区域空白

**解决方法：**
1. 检查 `result.chartData` 是否为空数组
2. 确保 `chartData` 中每个对象都包含 `name` 字段
3. 检查浏览器控制台是否有 Recharts 相关错误

---

## 📊 数据格式验证

### 后端返回格式检查清单

确保后端返回的数据符合以下格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "字符串",
    "status": "success" | "failed" | "running",
    "steps": [
      {
        "id": "字符串",
        "name": "字符串",
        "description": "字符串",
        "status": "success" | "failed" | "running" | "pending",
        "timestamp": "HH:mm:ss"
      }
    ],
    "logs": [
      {
        "id": "字符串",
        "toolName": "字符串",
        "inputParams": "JSON字符串",
        "outputResult": "JSON字符串（可选）",
        "status": "success" | "failed",
        "duration": "字符串（如 '850ms'）",
        "timestamp": "HH:mm:ss"
      }
    ],
    "result": {
      "summary": "字符串",
      "chartType": "line" | "bar" | "none",
      "chartData": [
        {
          "name": "字符串（必需）",
          // 其他数据字段
        }
      ],
      "rawData": [] // 可选
    }
  }
}
```

---

## 🔄 下一步：实现真实 Agent 逻辑

当前后端返回的是基于规则的数据（根据关键词判断意图）。要实现真正的智能调度，需要：

1. **实现 Agent 类**（`backend/app/core/agent.py`）
   - 接入大模型进行意图识别
   - 实现工具选择和参数提取
   - 实现多工具联动

2. **实现工具函数**（`backend/app/tools/`）
   - 对接真实 API（天气、新闻、股票等）
   - 实现数据处理逻辑
   - 实现文档生成逻辑

3. **优化提示词**（`backend/app/core/prompt.py`）
   - 设计更精确的意图识别提示词
   - 添加示例参考
   - 支持多轮对话

详细实现指南请参考：
- `docs/TOOL_GUIDE.md` - 工具开发指南
- `docs/API_SPEC.md` - API 接口规范
- `PROJECT_PLAN.md` - 项目规划

---

## ✅ 验证清单

测试完成后，确认以下项目：

- [ ] 后端服务正常启动
- [ ] 前端服务正常启动
- [ ] 前端能成功发送请求到后端
- [ ] 后端能正常响应请求
- [ ] 前端能正确解析后端返回的数据
- [ ] 工作流步骤正常显示
- [ ] 工具日志正常显示
- [ ] 结果数据正常展示
- [ ] 图表正常渲染
- [ ] 错误处理正常（测试错误场景）

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：前后端协同人员


