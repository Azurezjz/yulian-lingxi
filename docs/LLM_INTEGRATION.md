# 大模型接入指南

本文档说明如何为项目接入大模型，支持多种接入方式。

---

## 一、支持的接入方式

### 1. OpenAI API（推荐用于演示）

**优点：**
- 接入简单，只需 API Key
- 性能稳定，响应速度快
- 支持 GPT-3.5、GPT-4 等模型

**缺点：**
- 需要付费（有免费额度）
- 需要网络访问

### 2. 本地模型（推荐用于课设）

**优点：**
- 免费使用
- 数据隐私性好
- 适合演示

**缺点：**
- 需要本地部署模型
- 需要一定的硬件资源

**支持的本地模型：**
- Qwen（通义千问）
- ChatGLM
- 其他支持 OpenAI 兼容 API 的模型

### 3. 降级方案（无需大模型）

**说明：**
- 如果未配置大模型，系统会自动使用基于规则的意图识别
- 功能完整，适合演示

---

## 二、快速开始

### 方案 1：使用 OpenAI API

**步骤 1：获取 API Key**
1. 访问 https://platform.openai.com/
2. 注册账号并获取 API Key

**步骤 2：配置环境变量**
创建 `backend/.env` 文件：

```bash
LLM_API_KEY=sk-your-openai-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

**步骤 3：安装依赖**
```bash
pip install openai
```

**步骤 4：重启服务**
```bash
uvicorn app.main:app --reload
```

### 方案 2：使用本地模型

**步骤 1：部署本地模型服务**

以 Qwen 为例，使用 vLLM 部署：

```bash
# 安装 vLLM
pip install vllm

# 启动服务（OpenAI 兼容 API）
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen-7B-Chat \
    --port 8001
```

**步骤 2：配置环境变量**

创建 `backend/.env` 文件：

```bash
LLM_API_KEY=not-needed  # 如果不需要 API Key
LLM_BASE_URL=http://localhost:8001/v1
LLM_MODEL=Qwen/Qwen-7B-Chat
```

**步骤 3：安装依赖**
```bash
pip install openai
```

**步骤 4：重启服务**
```bash
uvicorn app.main:app --reload
```

### 方案 3：不使用大模型（降级方案）

**说明：**
- 不设置 `LLM_API_KEY` 或设置为空
- 系统会自动使用基于规则的意图识别
- 功能完整，适合演示

---

## 三、工作原理

### 1. 意图识别流程

```
用户输入
  ↓
Agent.execute()
  ↓
LLMService.chat()  →  调用大模型（如果配置）
  ↓                    ↓
解析 JSON 结果      降级到规则识别（如果失败）
  ↓
提取工具名称和参数
  ↓
调用工具
  ↓
返回结果
```

### 2. 降级机制

系统具有完善的降级机制：

1. **大模型不可用** → 自动使用规则识别
2. **大模型返回格式错误** → 自动使用规则识别
3. **大模型调用超时** → 自动使用规则识别

确保系统始终可用，不会因为大模型问题而崩溃。

---

## 四、提示词模板

系统使用提示词模板引导大模型进行意图识别，模板位于 `backend/app/core/prompt.py`。

**当前提示词结构：**
1. 系统角色定义
2. 可用工具列表（含功能描述和参数说明）
3. 用户需求
4. 返回格式要求（JSON）

**自定义提示词：**
可以修改 `PromptTemplate.INTENT_RECOGNITION_PROMPT` 来优化意图识别效果。

---

## 五、测试验证

### 测试大模型是否接入成功

**方法 1：查看日志**
启动服务后，查看控制台输出：
- 如果看到 "OpenAI API 调用失败" 或 "本地模型调用失败"，说明尝试调用大模型但失败
- 如果没有相关日志，说明使用了降级方案

**方法 2：测试意图识别**
输入一些复杂的自然语言：
- "我想知道北京明天会不会下雨"
- "帮我找一些关于人工智能的最新消息"
- "计算一下 123 乘以 456 等于多少"

如果大模型接入成功，这些复杂表达也能正确识别。

**方法 3：检查环境变量**
```bash
# 在 Python 中检查
from app.config import settings
print(settings.LLM_API_KEY)  # 应该显示你的 API Key
```

---

## 六、常见问题

### Q1: 大模型调用失败怎么办？

**A:** 系统会自动降级到规则识别，功能仍然可用。检查：
1. API Key 是否正确
2. 网络是否正常
3. 模型服务是否启动（本地模型）

### Q2: 如何切换不同的模型？

**A:** 修改 `.env` 文件中的 `LLM_MODEL` 配置：
```bash
LLM_MODEL=gpt-4  # 使用 GPT-4
# 或
LLM_MODEL=qwen-7b-chat  # 使用 Qwen
```

### Q3: 本地模型响应慢怎么办？

**A:** 
1. 使用更小的模型（如 Qwen-1.8B）
2. 使用量化模型（4-bit、8-bit）
3. 使用 GPU 加速

### Q4: 如何优化意图识别准确率？

**A:**
1. 优化提示词模板（`prompt.py`）
2. 添加更多示例到提示词
3. 使用更强的模型（如 GPT-4）

---

## 七、性能优化

### 1. 缓存机制（可选）

可以添加缓存机制，缓存常见查询的意图识别结果：

```python
# 在 Agent 类中添加缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def _cached_intent_recognition(self, user_input: str):
    # 缓存意图识别结果
    pass
```

### 2. 批量处理（可选）

对于多个请求，可以批量调用大模型：

```python
# 批量调用
responses = await asyncio.gather(*[
    self.llm_service.chat([{"role": "user", "content": input}])
    for input in inputs
])
```

---

## 八、安全注意事项

1. **API Key 安全**
   - 不要将 API Key 提交到 Git
   - 使用 `.env` 文件管理密钥
   - 生产环境使用环境变量或密钥管理服务

2. **输入验证**
   - 系统已对用户输入进行基本验证
   - 建议添加更严格的输入过滤

3. **速率限制**
   - OpenAI API 有速率限制
   - 建议添加请求限流机制

---

## 九、演示建议

### 课设演示场景

**场景 1：展示大模型能力**
- 输入："我想知道北京明天会不会下雨"
- 说明：大模型能理解自然语言，提取"北京"、"明天"、"天气"等关键信息

**场景 2：展示降级机制**
- 说明：即使大模型不可用，系统仍能正常工作
- 演示：关闭大模型服务，系统自动使用规则识别

**场景 3：对比效果**
- 规则识别：只能识别固定关键词
- 大模型识别：能理解复杂表达、同义词、上下文

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：后端开发团队


