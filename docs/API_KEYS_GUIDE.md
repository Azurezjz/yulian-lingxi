# API Key 获取指南

本文档说明如何获取各个工具所需的 API Key。

---

## 一、天气 API（和风天气）

### 1. 注册账号
1. 访问 https://dev.qweather.com/
2. 点击 "注册" 创建账号
3. 选择免费套餐（开发者版）

### 2. 获取 API Key
1. 登录后，进入 "控制台" → "应用管理"
2. 创建新应用，选择 "Web API"
3. 系统会生成一个 API Key
4. 复制该 Key

### 3. 配置
在 `backend/.env` 文件中添加：
```bash
WEATHER_API_KEY=your_qweather_api_key
```

### 4. 免费额度
- 每分钟 300 次请求
- 每天 5,000 次调用
- 支持7天天气预报
- 足够日常使用

### 5. 优势
- ✅ 中文支持更好
- ✅ 中国城市数据更准确
- ✅ API 响应速度快
- ✅ 免费额度充足

---

## 二、新闻 API（NewsAPI）

### 1. 注册账号
1. 访问 https://newsapi.org/
2. 点击 "Get API Key" 注册账号
3. 选择免费套餐（Developer plan）

### 2. 获取 API Key
1. 登录后，在 Dashboard 中可以看到 API Key
2. 复制该 Key

### 3. 配置
在 `backend/.env` 文件中添加：
```bash
NEWS_API_KEY=your_newsapi_key
```

### 4. 免费额度
- 每天 100 次请求
- 仅限开发使用
- 如需更多请求，需要升级到付费套餐

### 5. 注意事项
- 免费套餐仅支持 HTTP（非 HTTPS）
- 生产环境建议使用付费套餐

---

## 三、股票 API（Alpha Vantage）

### 1. 注册账号
1. 访问 https://www.alphavantage.co/support/#api-key
2. 填写邮箱和用途
3. 点击 "GET FREE API KEY"

### 2. 获取 API Key
1. 检查邮箱，会收到包含 API Key 的邮件
2. 复制该 Key

### 3. 配置
在 `backend/.env` 文件中添加：
```bash
STOCK_API_KEY=your_alphavantage_api_key
```

### 4. 免费额度
- 每分钟 5 次请求
- 每天 500 次调用
- 支持美国股票数据

### 5. 注意事项
- 主要支持美国股票（NYSE, NASDAQ）
- 中国股票需要使用其他 API（如新浪财经、腾讯财经等）

---

## 四、不使用真实 API（Mock 数据）

如果不想配置 API Key，系统会自动使用 Mock 数据：

- **天气**：基于城市和日期生成确定性数据
- **新闻**：使用预设的新闻模板
- **股票**：基于股票代码生成模拟数据

Mock 数据的特点：
- ✅ 无需注册和配置
- ✅ 响应速度快
- ✅ 数据格式一致
- ❌ 不是真实数据
- ❌ 仅用于演示和测试

---

## 五、配置示例

完整的 `.env` 文件示例：

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 大模型配置（可选）
# LLM_API_KEY=sk-your-openai-api-key
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-3.5-turbo

# 工具 API 配置（可选，不配置则使用 Mock 数据）
WEATHER_API_KEY=your_openweathermap_api_key
NEWS_API_KEY=your_newsapi_key
STOCK_API_KEY=your_alphavantage_api_key

# 工具调用配置
TOOL_TIMEOUT=10
MAX_TOOL_STEPS=4
```

---

## 六、验证配置

配置完成后，重启后端服务，查看日志：

- 如果看到 "天气 API 调用失败"，说明 API Key 可能无效
- 如果看到 "使用 Mock 数据"，说明未配置 API Key 或 API 调用失败

---

## 七、常见问题

### Q1: API Key 无效怎么办？

**A:** 
1. 检查 API Key 是否正确复制（注意前后空格）
2. 确认 API Key 是否已激活（某些 API 需要等待几分钟）
3. 检查 API 使用额度是否已用完

### Q2: 如何测试 API Key 是否有效？

**A:** 
可以使用 curl 或 Postman 测试：

```bash
# 测试天气 API
curl "http://api.openweathermap.org/data/2.5/weather?q=Beijing&appid=YOUR_API_KEY"

# 测试新闻 API
curl "https://newsapi.org/v2/everything?q=AI&apiKey=YOUR_API_KEY"

# 测试股票 API
curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=YOUR_API_KEY"
```

### Q3: 可以同时使用真实 API 和 Mock 数据吗？

**A:** 
可以。系统会优先尝试使用真实 API，如果失败则自动降级到 Mock 数据。每个工具独立判断。

### Q4: 中国股票数据如何获取？

**A:** 
Alpha Vantage 主要支持美国股票。对于中国股票，可以：
1. 使用其他免费 API（如新浪财经、腾讯财经的公开接口）
2. 使用付费 API（如聚宽、米筐等）
3. 暂时使用 Mock 数据

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：后端开发团队

