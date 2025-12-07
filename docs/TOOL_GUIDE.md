# 工具开发指南

本文档为**工具开发人员**提供详细的工具封装规范，确保所有工具接口统一、可复用、易维护。

## 一、工具开发原则

### 1. 统一接口规范
所有工具必须遵循统一的输入输出格式，便于调度层调用。

### 2. 错误处理
- 所有工具函数必须包含异常捕获
- 返回统一的错误格式
- 提供降级方案（如返回模拟数据）

### 3. 参数校验
- 在函数入口处校验必需参数
- 提供清晰的错误提示

### 4. 日志记录
- 记录工具调用开始/结束时间
- 记录输入参数和输出结果（脱敏处理）

---

## 二、工具接口规范

### 基础接口定义

所有工具函数必须遵循以下接口：

```python
from typing import Dict, Any, Optional

def tool_name(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    工具功能描述
    
    Args:
        params: 参数字典，包含工具所需的所有参数
        
    Returns:
        {
            "success": bool,           # 是否成功
            "data": Any,               # 返回数据
            "error": Optional[str],    # 错误信息（失败时）
            "metadata": {              # 元数据
                "tool_name": str,
                "duration": str,
                "timestamp": str
            }
        }
    """
    pass
```

### 返回格式说明

**成功响应：**
```python
{
    "success": True,
    "data": {
        # 工具特定的数据结构
    },
    "error": None,
    "metadata": {
        "tool_name": "weather",
        "duration": "850ms",
        "timestamp": "2024-01-01 10:30:18"
    }
}
```

**失败响应：**
```python
{
    "success": False,
    "data": None,
    "error": "参数错误：location 不能为空",
    "metadata": {
        "tool_name": "weather",
        "duration": "50ms",
        "timestamp": "2024-01-01 10:30:18"
    }
}
```

---

## 三、5 类工具详细规范

### 1. 生活服务工具：天气查询

**文件路径**：`backend/app/tools/weather.py`

**函数名**：`get_weather`

**参数说明：**
```python
params = {
    "location": str,      # 必填：城市名称（如 "北京"、"Guangzhou"）
    "days": int          # 可选：查询天数（默认 7，最大 7）
}
```

**返回数据格式：**
```python
{
    "success": True,
    "data": {
        "location": "北京",
        "forecast": [
            {
                "date": "2024-01-01",
                "weather": "Sunny",
                "maxTemp": 25,
                "minTemp": 18,
                "humidity": 65,
                "wind": "South 2-3"
            },
            # ... 更多日期
        ]
    },
    "error": None,
    "metadata": {...}
}
```

**API 资源推荐：**
- OpenWeatherMap: https://openweathermap.org/api
- 和风天气: https://dev.qweather.com/

**示例代码：**
```python
import httpx
from typing import Dict, Any

def get_weather(params: Dict[str, Any]) -> Dict[str, Any]:
    """天气查询工具"""
    import time
    start_time = time.time()
    
    # 参数校验
    location = params.get("location")
    if not location:
        return {
            "success": False,
            "data": None,
            "error": "参数错误：location 不能为空",
            "metadata": {
                "tool_name": "weather",
                "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    days = params.get("days", 7)
    
    try:
        # 调用天气 API
        # response = httpx.get(f"https://api.openweathermap.org/...")
        # data = response.json()
        
        # 返回格式化的数据
        return {
            "success": True,
            "data": {
                "location": location,
                "forecast": [...]  # 格式化后的预报数据
            },
            "error": None,
            "metadata": {
                "tool_name": "weather",
                "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"API 调用失败：{str(e)}",
            "metadata": {...}
        }
```

---

### 2. 信息检索工具：新闻检索

**文件路径**：`backend/app/tools/news.py`

**函数名**：`search_news`

**参数说明：**
```python
params = {
    "query": str,         # 必填：搜索关键词
    "limit": int,         # 可选：返回数量（默认 10，最大 50）
    "category": str       # 可选：分类（如 "technology"、"business"）
}
```

**返回数据格式：**
```python
{
    "success": True,
    "data": {
        "articles": [
            {
                "title": "OpenAI Releases GPT-5 Preview",
                "source": "TechCrunch",
                "url": "https://...",
                "publishedAt": "2024-01-01T10:00:00Z",
                "description": "新闻摘要..."
            },
            # ... 更多新闻
        ],
        "total": 10
    },
    "error": None,
    "metadata": {...}
}
```

**API 资源推荐：**
- NewsAPI: https://newsapi.org/
- 百度新闻 API

---

### 3. 数据处理工具：股票数据查询

**文件路径**：`backend/app/tools/stock.py`

**函数名**：`get_stock_data`

**参数说明：**
```python
params = {
    "symbol": str,        # 必填：股票代码（如 "000001"、"AAPL"）
    "days": int           # 可选：查询天数（默认 5）
}
```

**返回数据格式：**
```python
{
    "success": True,
    "data": {
        "symbol": "000001",
        "name": "平安银行",
        "prices": [
            {
                "date": "2024-01-01",
                "open": 10.5,
                "close": 10.8,
                "high": 11.0,
                "low": 10.3,
                "volume": 1000000
            },
            # ... 更多日期
        ]
    },
    "error": None,
    "metadata": {...}
}
```

**API 资源推荐：**
- Alpha Vantage: https://www.alphavantage.co/
- Yahoo Finance API
- 新浪财经 API（免费）

---

### 4. 数据处理工具：数值计算

**文件路径**：`backend/app/tools/data.py`

**函数名**：`calculate`

**参数说明：**
```python
params = {
    "expression": str,    # 必填：计算表达式（如 "2 + 3 * 4"）
    "variables": dict     # 可选：变量字典（如 {"x": 10, "y": 20}）
}
```

**返回数据格式：**
```python
{
    "success": True,
    "data": {
        "expression": "2 + 3 * 4",
        "result": 14,
        "steps": ["2 + 3 * 4", "2 + 12", "14"]  # 可选：计算步骤
    },
    "error": None,
    "metadata": {...}
}
```

**实现建议：**
- 使用 `eval()` 需谨慎，建议使用 `ast.literal_eval()` 或数学表达式解析库
- 或使用 `sympy` 库进行符号计算

---

### 5. 文档生成工具

**文件路径**：`backend/app/tools/document.py`

**函数名**：`generate_document`

**参数说明：**
```python
params = {
    "template": str,      # 必填：文档模板类型（如 "report"、"email"、"summary"）
    "content": str,        # 必填：内容提示（如 "基于天气数据写出行建议"）
    "data": dict,         # 可选：上下文数据（如之前的工具执行结果）
    "format": str         # 可选：输出格式（"markdown" / "text"，默认 "markdown"）
}
```

**返回数据格式：**
```python
{
    "success": True,
    "data": {
        "content": "# 北京周末出行建议\n\n根据天气数据...",
        "format": "markdown",
        "word_count": 500
    },
    "error": None,
    "metadata": {...}
}
```

**实现建议：**
- 使用大模型生成文档内容
- 支持 Markdown 格式输出
- 可扩展支持 Word 文档生成（使用 `python-docx`）

---

## 四、工具注册与调用

### 工具注册表

在 `backend/app/tools/__init__.py` 中注册所有工具：

```python
from .weather import get_weather
from .news import search_news
from .stock import get_stock_data
from .data import calculate
from .document import generate_document

TOOLS_REGISTRY = {
    "weather": {
        "function": get_weather,
        "description": "天气查询工具，支持7天预报",
        "required_params": ["location"],
        "optional_params": ["days"]
    },
    "news": {
        "function": search_news,
        "description": "新闻检索工具",
        "required_params": ["query"],
        "optional_params": ["limit", "category"]
    },
    "stock": {
        "function": get_stock_data,
        "description": "股票数据查询工具",
        "required_params": ["symbol"],
        "optional_params": ["days"]
    },
    "calculate": {
        "function": calculate,
        "description": "数值计算工具",
        "required_params": ["expression"],
        "optional_params": ["variables"]
    },
    "document": {
        "function": generate_document,
        "description": "文档生成工具",
        "required_params": ["template", "content"],
        "optional_params": ["data", "format"]
    }
}
```

### 工具调用示例

```python
from app.tools import TOOLS_REGISTRY

# 调用天气工具
tool_info = TOOLS_REGISTRY["weather"]
result = tool_info["function"]({
    "location": "北京",
    "days": 7
})

if result["success"]:
    print(result["data"])
else:
    print(f"错误：{result['error']}")
```

---

## 五、降级方案（Mock 数据）

当外部 API 不可用时，工具应返回模拟数据，确保演示不中断。

### Mock 数据示例（天气工具）

```python
def get_weather_mock(location: str, days: int = 7) -> Dict[str, Any]:
    """天气工具 Mock 数据"""
    import random
    from datetime import datetime, timedelta
    
    forecast = []
    base_temp = 20
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        forecast.append({
            "date": date,
            "weather": random.choice(["Sunny", "Cloudy", "Rainy"]),
            "maxTemp": base_temp + random.randint(-5, 10),
            "minTemp": base_temp + random.randint(-10, 0),
            "humidity": random.randint(40, 80),
            "wind": f"{random.choice(['North', 'South', 'East', 'West'])} {random.randint(2, 5)}"
        })
    
    return {
        "success": True,
        "data": {
            "location": location,
            "forecast": forecast
        },
        "error": None,
        "metadata": {
            "tool_name": "weather",
            "duration": "50ms",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_mock": True  # 标记为 Mock 数据
        }
    }
```

---

## 六、测试要求

### 单元测试

每个工具函数都应编写单元测试：

```python
# tests/test_weather.py
import pytest
from app.tools.weather import get_weather

def test_get_weather_success():
    result = get_weather({"location": "北京", "days": 3})
    assert result["success"] is True
    assert "forecast" in result["data"]
    assert len(result["data"]["forecast"]) == 3

def test_get_weather_missing_location():
    result = get_weather({"days": 3})
    assert result["success"] is False
    assert "location" in result["error"].lower()
```

### 集成测试

测试工具与调度层的集成：

```python
# tests/test_integration.py
def test_workflow_with_weather_tool():
    # 模拟完整工作流
    pass
```

---

## 七、开发检查清单

工具开发完成后，请确认：

- [ ] 函数接口符合规范（统一的输入输出格式）
- [ ] 参数校验完整（必需参数检查）
- [ ] 错误处理完善（异常捕获、错误返回）
- [ ] 日志记录完整（调用时间、参数、结果）
- [ ] Mock 数据可用（API 失败时的降级方案）
- [ ] 单元测试通过
- [ ] 文档注释完整（函数说明、参数说明）
- [ ] 已在 `TOOLS_REGISTRY` 中注册

---

**文档版本**：v1.0  
**最后更新**：2024年  
**维护者**：工具开发人员


