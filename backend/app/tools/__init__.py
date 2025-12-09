"""
工具注册表

所有工具必须在此注册，才能被调度层调用。
"""
from typing import Dict, Any
from .weather import get_weather
from .news import search_news
from .stock import get_stock_data
from .data import calculate
from .document import generate_document

# 工具注册表
TOOLS_REGISTRY: Dict[str, Dict[str, Any]] = {
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

