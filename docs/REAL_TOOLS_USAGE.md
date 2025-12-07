# 真实工具调用使用说明

## ✅ 已完成的改进

### 1. 工具注册
- ✅ 所有工具已注册到 `backend/app/tools/__init__.py`
- ✅ 工具包括：weather、news、stock、calculate、document

### 2. 工具函数改进
- ✅ **天气工具**：根据城市和天数生成不同的天气数据
- ✅ **新闻工具**：根据查询关键词返回相关新闻
- ✅ **计算工具**：实现真实的数学计算功能
- ✅ **股票工具**：支持股票代码和天数参数
- ✅ **文档工具**：支持不同模板类型

### 3. 后端路由改进
- ✅ 后端路由现在调用真实的工具函数
- ✅ 改进了参数提取逻辑，支持更多城市和参数
- ✅ 根据用户输入自动识别意图并提取参数

---

## 🎯 功能说明

### 天气查询

**支持的输入格式：**
- "查北京天气"
- "天津现在的天气"
- "广州近7天天气"
- "上海未来3天天气"

**支持的城市：**
北京、上海、广州、深圳、杭州、南京、成都、武汉、西安、天津、重庆、苏州、长沙、郑州、青岛、大连、济南、福州、厦门、合肥、石家庄、哈尔滨、长春、沈阳

**参数提取：**
- 自动识别城市名称
- 自动提取天数（1-7天）

**返回数据：**
- 根据城市生成不同的基础温度
- 根据天数返回对应数量的预报数据
- 包含温度、湿度、天气状况、风力等信息

---

### 新闻检索

**支持的输入格式：**
- "查最近的 AI 新闻"
- "检索科技资讯"
- "找3条财经新闻"
- "搜索人工智能相关新闻"

**参数提取：**
- 自动提取查询关键词
- 自动提取数量（1-50条）

**返回数据：**
- 根据关键词返回相关新闻
- 支持 AI、科技、财经等类别
- 包含标题、来源、发布时间、摘要等信息

---

### 股票数据查询

**支持的输入格式：**
- "查贵州茅台股票"
- "查询000001近5日数据"
- "看看平安银行股票"

**参数提取：**
- 自动识别股票代码（6位数字）
- 自动识别股票名称（茅台、平安等）
- 自动提取天数（1-30天）

**返回数据：**
- 股票代码、名称
- 历史价格数据（开盘、收盘、最高、最低、成交量）

---

### 数值计算

**支持的输入格式：**
- "计算 2 + 3 * 4"
- "算一下 100 - 50"
- "2 * 5 等于多少"

**参数提取：**
- 自动提取数学表达式
- 移除"计算"、"算"等无关词汇

**返回数据：**
- 计算结果
- 计算步骤

**安全特性：**
- 只允许数字和基本运算符
- 不允许执行任意代码

---

### 文档生成

**支持的输入格式：**
- "生成一份报告"
- "写一封邮件"
- "创建一个总结"

**参数提取：**
- 自动识别模板类型（report、email、summary）
- 提取内容提示

**返回数据：**
- 生成的文档内容
- 文档格式（markdown/text）
- 字数统计

---

## 🧪 测试示例

### 测试天气查询

```bash
# 测试不同城市
curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "查北京天气"}'

curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "天津现在的天气"}'

curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "广州近7天天气"}'
```

### 测试新闻检索

```bash
curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "查最近的 AI 新闻"}'

curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "找5条科技新闻"}'
```

### 测试计算功能

```bash
curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "计算 2 + 3 * 4"}'
```

---

## 🔍 验证方法

### 1. 检查是否调用真实工具

**方法：** 查看后端日志或工具调用日志

在工具日志中应该看到：
- `toolName`: 工具名称（如 "WEATHER"、"NEWS"）
- `inputParams`: 实际传入的参数（如 `{"location": "天津", "days": 7}`）
- `duration`: 工具执行时间

### 2. 验证数据是否不同

**测试步骤：**
1. 输入："查北京天气"
2. 记录返回的数据
3. 输入："查天津天气"
4. 对比两次返回的数据

**预期结果：**
- 城市名称不同（北京 vs 天津）
- 温度数据不同（不同城市的基础温度不同）
- 日期数据不同（基于当前日期生成）

### 3. 验证参数提取

**测试步骤：**
1. 输入："查广州近3天天气"
2. 查看工具日志中的 `inputParams`

**预期结果：**
```json
{
  "location": "广州",
  "days": 3
}
```

---

## 📊 数据格式

### 工具返回格式

所有工具返回统一格式：

```json
{
  "success": true,
  "data": {
    // 工具特定的数据
  },
  "error": null,
  "metadata": {
    "tool_name": "weather",
    "duration": "50ms",
    "timestamp": "2024-01-01 10:30:18",
    "is_mock": true  // 标记是否为 Mock 数据
  }
}
```

### 前端接收格式

后端将工具返回的数据转换为前端需要的格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "...",
    "status": "success",
    "steps": [...],
    "logs": [...],
    "result": {
      "summary": "...",
      "chartType": "line" | "bar" | "none",
      "chartData": [...],
      "rawData": [...]
    }
  }
}
```

---

## 🚀 下一步：接入真实 API

当前工具返回的是基于参数的 Mock 数据。要接入真实 API，需要：

### 1. 天气 API
- 申请 OpenWeatherMap API Key
- 或使用和风天气 API
- 在 `backend/app/tools/weather.py` 中实现真实 API 调用

### 2. 新闻 API
- 申请 NewsAPI Key
- 或使用百度新闻 API
- 在 `backend/app/tools/news.py` 中实现真实 API 调用

### 3. 股票 API
- 使用 Alpha Vantage API
- 或使用新浪财经 API
- 在 `backend/app/tools/stock.py` 中实现真实 API 调用

### 4. 文档生成
- 接入大模型 API（如 OpenAI、Qwen 等）
- 在 `backend/app/tools/document.py` 中实现文档生成逻辑

---

## ⚠️ 注意事项

1. **Mock 数据标记**：当前所有工具返回的数据都标记为 `"is_mock": true`，表示这是模拟数据
2. **参数验证**：工具函数会验证必需参数，缺少参数会返回错误
3. **错误处理**：工具调用失败时，会返回错误信息，不会导致系统崩溃
4. **性能**：当前工具函数是同步的，在异步上下文中调用，性能足够

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：后端开发团队


