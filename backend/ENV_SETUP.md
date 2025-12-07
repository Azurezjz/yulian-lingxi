# 环境变量配置说明

## 创建 .env 文件

在 `backend/` 目录下创建 `.env` 文件，配置以下内容：

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 大模型配置
# 方案1：使用阿里云百炼平台（DashScope）API（推荐）
# 申请地址：https://bailian.console.aliyun.com/
LLM_API_KEY=sk-your-dashscope-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
# 可选模型：qwen-turbo, qwen-plus, qwen-max, qwen2.5-7b-instruct

# 方案2：使用 OpenAI API
# LLM_API_KEY=sk-your-openai-api-key
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-3.5-turbo

# 方案3：使用本地模型（如 Qwen、ChatGLM 等）
# LLM_API_KEY=not-needed
# LLM_BASE_URL=http://localhost:8001/v1
# LLM_MODEL=qwen-7b-chat

# 方案4：不使用大模型（使用规则识别）
# 不设置 LLM_API_KEY 或留空

# 工具 API 配置（可选，如果不配置则使用 Mock 数据）
# 天气 API - 和风天气（免费注册：https://dev.qweather.com/）
WEATHER_API_KEY=94a92bb92e9d4348adae868b20b63f0c

# 新闻 API - NewsAPI（免费注册：https://newsapi.org/）
NEWS_API_KEY=your_newsapi_key

# 股票 API - Alpha Vantage（免费注册：https://www.alphavantage.co/support/#api-key）
STOCK_API_KEY=your_alphavantage_api_key

# 工具调用配置
TOOL_TIMEOUT=10
MAX_TOOL_STEPS=4
```

## 快速测试

### 不使用大模型（默认）
不设置 `LLM_API_KEY`，系统会自动使用规则识别。

### 使用阿里云百炼平台（DashScope）API（推荐）

**优点：**
- ✅ 国内访问稳定
- ✅ 中文支持好
- ✅ 有免费额度
- ✅ 价格相对较低

**配置步骤：**

1. **申请 API Key**
   - 访问：https://bailian.console.aliyun.com/
   - 注册/登录阿里云账号
   - 创建 API Key（格式：`sk-...`）

2. **设置环境变量**
   ```bash
   LLM_API_KEY=sk-your-dashscope-api-key
   LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   LLM_MODEL=qwen-turbo
   ```
   
   **可选模型：**
   - `qwen-turbo` - 快速版本（推荐）
   - `qwen-plus` - 增强版本
   - `qwen-max` - 最强版本
   - `qwen2.5-7b-instruct` - 7B 指令版本

3. **地域选择**
   - 中国大陆：`https://dashscope.aliyuncs.com/compatible-mode/v1`
   - 国际（新加坡）：`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
   
   ⚠️ **重要**：API Key 和 Base URL 的地域必须匹配！

4. **安装依赖**
   ```bash
   pip install openai
   ```

5. **测试配置**
   ```bash
   python test_llm.py
   ```

6. **重启服务**
   ```bash
   uvicorn app.main:app --reload
   ```

### 使用 OpenAI API
1. 获取 API Key：https://platform.openai.com/
2. 设置环境变量：
   ```bash
   LLM_API_KEY=sk-your-key
   LLM_BASE_URL=https://api.openai.com/v1
   LLM_MODEL=gpt-3.5-turbo
   ```
3. 安装依赖：`pip install openai`
4. 重启服务

### 使用本地模型
1. 部署本地模型服务（支持 OpenAI 兼容 API）
2. 设置环境变量：
   ```bash
   LLM_BASE_URL=http://localhost:8001/v1
   LLM_MODEL=your-model-name
   ```
3. 安装依赖：`pip install openai`
4. 重启服务

## 测试大模型配置

运行测试脚本验证配置：

```bash
python test_llm.py
```

测试脚本会检查：
- ✅ 配置是否正确
- ✅ API Key 是否有效
- ✅ 大模型是否能正常调用
- ✅ Agent 意图识别是否正常

详细说明请参考：`docs/LLM_INTEGRATION.md`

