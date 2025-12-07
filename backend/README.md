# 后端开发指南

## 一、环境准备

### 1. Python 环境

推荐使用 Python 3.9+，使用 conda 或 venv 创建虚拟环境：

```bash
# 使用 conda
conda create -n lingxi_backend python=3.9 -y
conda activate lingxi_backend

# 或使用 venv
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```bash
# 大模型配置
LLM_API_KEY=your_api_key
LLM_BASE_URL=http://localhost:8001  # 本地模型地址

# 工具 API 配置
WEATHER_API_KEY=your_weather_api_key
NEWS_API_KEY=your_news_api_key
STOCK_API_KEY=your_stock_api_key

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 二、项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   │
│   ├── core/                # 核心调度层
│   │   ├── __init__.py
│   │   ├── agent.py         # Agent 调度逻辑
│   │   ├── prompt.py        # 提示词模板
│   │   └── scheduler.py     # 工具调度器
│   │
│   ├── tools/               # 工具执行层
│   │   ├── __init__.py      # 工具注册表
│   │   ├── weather.py       # 天气查询工具
│   │   ├── news.py          # 新闻检索工具
│   │   ├── stock.py         # 股票数据工具
│   │   ├── data.py          # 数据处理工具
│   │   └── document.py      # 文档生成工具
│   │
│   └── api/                 # API 路由
│       ├── __init__.py
│       └── routes.py        # 路由定义
│
├── tests/                   # 测试文件
│   ├── __init__.py
│   ├── test_tools.py
│   └── test_api.py
│
├── .env.example             # 环境变量示例
├── requirements.txt         # 依赖包
└── README.md               # 本文档
```

## 三、快速开始

### 1. 启动开发服务器

```bash
# 方式一：使用 uvicorn 直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式二：使用 Python 启动
python -m app.main
```

### 2. 访问 API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 测试接口

```bash
# 使用 curl 测试
curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"userInput": "查北京天气"}'
```

## 四、开发流程

### 1. 工具开发

参考 `docs/TOOL_GUIDE.md`，按照规范开发工具函数。

**步骤：**
1. 在 `app/tools/` 目录下创建工具文件（如 `weather.py`）
2. 实现工具函数，遵循统一接口规范
3. 在 `app/tools/__init__.py` 中注册工具
4. 编写单元测试

### 2. 调度层开发

参考 `docs/API_SPEC.md`，实现意图识别和工具调度逻辑。

**步骤：**
1. 在 `app/core/prompt.py` 中设计提示词模板
2. 在 `app/core/agent.py` 中实现 Agent 逻辑
3. 在 `app/core/scheduler.py` 中实现工具调度器

### 3. API 开发

在 `app/api/routes.py` 中定义 API 路由，确保响应格式符合 `docs/API_SPEC.md` 规范。

## 五、注意事项

### 1. 数据格式

- **严格按照** `docs/API_SPEC.md` 定义的格式返回数据
- 字段名必须完全一致（区分大小写）
- 时间格式统一使用 `HH:mm:ss`

### 2. 错误处理

- 所有异常必须捕获，返回统一错误格式
- 工具调用失败时，优先返回 Mock 数据，确保演示不中断

### 3. 日志记录

- 记录关键操作（工具调用、API 请求）
- 敏感信息（API Key）不要记录到日志

### 4. 性能优化

- 工具调用设置超时时间（建议 10 秒）
- 使用异步请求（httpx.AsyncClient）提升并发性能

## 六、测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_tools.py

# 显示详细输出
pytest -v
```

### 测试覆盖率

```bash
pytest --cov=app --cov-report=html
```

## 七、部署

### 生产环境启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署（可选）

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：后端开发团队


