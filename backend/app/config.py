"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 大模型配置
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"  # 或本地模型名称
    
    # 工具 API 配置
    # 天气 API 配置（支持心知天气和和风天气）
    WEATHER_API_UID: Optional[str] = None  # 心知天气公钥（uid），优先使用
    WEATHER_API_SECRET: Optional[str] = None  # 心知天气私钥（key）
    WEATHER_API_KEY: Optional[str] = None  # 和风天气 API Key（降级方案）
    
    # 其他工具 API 配置
    NEWS_API_KEY: Optional[str] = None
    STOCK_API_KEY: Optional[str] = None
    
    # 工具调用配置
    TOOL_TIMEOUT: int = 10  # 工具调用超时时间（秒）
    MAX_TOOL_STEPS: int = 4  # 最大工具调用步骤数
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


