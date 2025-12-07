"""
大模型服务抽象层
支持多种大模型接入方式：OpenAI API、本地模型等
"""
from typing import Dict, Any, Optional
import json
import re
import asyncio
from app.config import settings

class LLMService:
    """大模型服务抽象类"""
    
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self._client = None
    
    async def chat(self, messages: list, temperature: float = 0.7, user_input: str = None) -> str:
        """
        调用大模型进行对话
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性
            user_input: 原始用户输入（用于降级方案）
            
        Returns:
            模型返回的文本内容
        """
        # 如果没有配置 API Key，使用降级方案（基于规则的识别）
        if not self.api_key:
            # 如果提供了原始用户输入，直接使用；否则从 messages 中提取
            if user_input:
                result = self._fallback_response_direct(user_input)
            else:
                result = self._fallback_response(messages)
            print(f"[DEBUG] LLM 降级方案 - 用户输入: {user_input or (messages[-1]['content'][:50] if messages else '')}, 返回: {result[:100] if result else ''}")
            return result
        
        # 根据配置选择不同的实现
        if self.base_url and "localhost" in self.base_url or "127.0.0.1" in self.base_url:
            # 本地模型
            return await self._call_local_model(messages, temperature)
        else:
            # OpenAI 兼容 API
            return await self._call_openai_api(messages, temperature)
    
    async def _call_openai_api(self, messages: list, temperature: float) -> str:
        """调用 OpenAI 兼容 API（支持 DashScope/百炼平台）"""
        try:
            from openai import OpenAI
            
            # 如果没有配置 base_url，使用默认的 DashScope 端点
            base_url = self.base_url
            if not base_url:
                # 默认使用阿里云 DashScope 的 OpenAI 兼容模式
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                print(f"[DEBUG] 未配置 LLM_BASE_URL，使用默认 DashScope 端点: {base_url}")
            
            if not self._client:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=base_url
                )
                print(f"[DEBUG] 初始化 OpenAI 客户端 - base_url: {base_url}, model: {self.model}")
            
            # 检查是否需要 JSON 格式（如果提示词中包含 JSON 要求）
            use_json_format = False
            for msg in messages:
                if "content" in msg:
                    content = msg["content"]
                    if isinstance(content, str) and ("json" in content.lower() or "返回格式" in content or "JSON" in content):
                        use_json_format = True
                        break
            
            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            if use_json_format:
                request_params["response_format"] = {"type": "json_object"}
                print(f"[DEBUG] 使用 JSON 格式响应模式")
            
            print(f"[DEBUG] 调用大模型 API - model: {self.model}, messages_count: {len(messages)}")
            
            response = self._client.chat.completions.create(**request_params)
            
            result = response.choices[0].message.content
            print(f"[DEBUG] 大模型 API 调用成功 - 返回长度: {len(result)} 字符")
            return result
            
        except ImportError:
            error_msg = "请安装 openai 库：pip install openai"
            print(f"[ERROR] {error_msg}")
            raise ImportError(error_msg)
        except asyncio.CancelledError:
            # 请求被取消（通常是服务器关闭或重启），使用降级方案
            print("[WARN] 大模型 API 请求被取消，使用降级方案")
            return self._fallback_response(messages)
        except Exception as e:
            error_detail = str(e)
            print(f"[ERROR] 大模型 API 调用失败：{error_detail}")
            print(f"[ERROR] 配置信息 - base_url: {self.base_url or '未配置'}, model: {self.model}")
            
            # 如果是认证错误，提供更详细的提示
            if "401" in error_detail or "unauthorized" in error_detail.lower() or "authentication" in error_detail.lower():
                print("[ERROR] API Key 认证失败，请检查：")
                print("  1. API Key 是否正确（从 https://bailian.console.aliyun.com/ 获取）")
                print("  2. API Key 是否已激活")
                print("  3. base_url 和 API Key 的地域是否匹配")
                print("  4. 中国大陆地域: https://dashscope.aliyuncs.com/compatible-mode/v1")
                print("  5. 国际地域: https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
            
            # 降级到规则识别
            return self._fallback_response(messages)
    
    async def _call_local_model(self, messages: list, temperature: float) -> str:
        """调用本地模型（通过 HTTP API）"""
        try:
            import httpx
            
            # 构建请求
            url = f"{self.base_url}/v1/chat/completions"
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"本地模型调用失败：{e}")
            # 降级到规则识别
            return self._fallback_response(messages)
    
    def _fallback_response_direct(self, user_input: str) -> str:
        """
        降级方案：基于规则的意图识别（直接使用用户输入）
        当大模型不可用时使用此方法
        """
        user_input_lower = user_input.lower()
        
        # 简单的规则识别（按优先级顺序检查）
        # 检查新闻相关关键词（必须明确包含"新闻"或"资讯"）
        if "新闻" in user_input_lower or "资讯" in user_input_lower or "news" in user_input_lower:
            # 提取查询关键词
            query = user_input
            # 移除常见动词
            query = re.sub(r'抓取|检索|搜索|找|看看|查|列出|总结|最近的', '', query)
            query = re.sub(r'新闻|资讯|news|条', '', query, flags=re.IGNORECASE)
            query = query.strip()
            
            # 提取数量
            limit = 10
            limit_match = re.search(r'(\d+)\s*条', user_input)
            if limit_match:
                limit = int(limit_match.group(1))
                limit = min(max(limit, 1), 50)
            
            # 提取领域关键词
            if not query or len(query) < 2:
                # 尝试提取领域关键词
                if "ai" in user_input_lower or "人工智能" in user_input_lower:
                    query = "AI"
                elif "科技" in user_input_lower:
                    query = "科技"
                elif "国内" in user_input_lower:
                    query = "国内"
                else:
                    query = "科技"  # 默认
            
            return json.dumps({
                "tool": "news",
                "parameters": {"query": query, "limit": limit},
                "reasoning": "用户查询新闻信息"
            })
        # 然后检查天气
        elif "天气" in user_input_lower or "气温" in user_input_lower or "weather" in user_input_lower:
            # 提取城市
            cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", 
                     "西安", "天津", "重庆", "苏州", "长沙", "郑州", "青岛", "大连"]
            location = "北京"
            for city in cities:
                if city in user_input:
                    location = city
                    break
            
            days = 7
            if any(kw in user_input_lower for kw in ["现在", "今天", "当前"]):
                days = 1
            else:
                # 尝试提取天数
                days_match = re.search(r'(\d+)\s*天', user_input)
                if days_match:
                    days = int(days_match.group(1))
                    days = min(max(days, 1), 7)
            
            return json.dumps({
                "tool": "weather",
                "parameters": {"location": location, "days": days},
                "reasoning": "用户查询天气信息"
            })
        elif "股票" in user_input_lower:
            return json.dumps({
                "tool": "stock",
                "parameters": {"symbol": "000001", "days": 5},
                "reasoning": "用户查询股票信息"
            })
        elif "计算" in user_input_lower or "+" in user_input or "-" in user_input:
            return json.dumps({
                "tool": "calculate",
                "parameters": {"expression": user_input},
                "reasoning": "用户需要进行计算"
            })
        else:
            return json.dumps({
                "tool": None,
                "reasoning": "无法识别用户意图，使用默认处理"
            })
    
    def _fallback_response(self, messages: list) -> str:
        """
        降级方案：基于规则的意图识别（从 messages 中提取）
        当大模型不可用时使用此方法
        """
        # 从消息中提取用户的实际输入
        # 如果 messages[-1]["content"] 是完整的提示词，尝试提取"用户需求："后面的内容
        content = messages[-1]["content"] if messages else ""
        
        # 尝试从提示词中提取用户的实际输入
        user_input = content
        if "用户需求：" in content:
            # 提取"用户需求："后面的内容
            match = re.search(r'用户需求[：:]\s*(.+?)(?:\n返回格式|$)', content, re.DOTALL)
            if match:
                user_input = match.group(1).strip()
        
        # 调用直接版本
        return self._fallback_response_direct(user_input)
        
        # 简单的规则识别（按优先级顺序检查）
        # 检查新闻相关关键词（必须明确包含"新闻"或"资讯"）
        if "新闻" in user_input_lower or "资讯" in user_input_lower or "news" in user_input_lower:
            # 提取查询关键词
            query = user_input
            # 移除常见动词
            query = re.sub(r'抓取|检索|搜索|找|看看|查|列出|总结', '', query)
            query = re.sub(r'新闻|资讯|news', '', query, flags=re.IGNORECASE)
            query = query.strip()
            
            # 提取数量
            limit = 10
            limit_match = re.search(r'(\d+)\s*条', user_input)
            if limit_match:
                limit = int(limit_match.group(1))
                limit = min(max(limit, 1), 50)
            
            # 提取领域关键词
            if not query or len(query) < 2:
                # 尝试提取领域关键词
                if "ai" in user_input_lower or "人工智能" in user_input_lower:
                    query = "AI"
                elif "科技" in user_input_lower:
                    query = "科技"
                elif "国内" in user_input_lower:
                    query = "国内"
                else:
                    query = "科技"  # 默认
            
            return json.dumps({
                "tool": "news",
                "parameters": {"query": query, "limit": limit},
                "reasoning": "用户查询新闻信息"
            })
        # 然后检查天气
        elif "天气" in user_input_lower or "气温" in user_input_lower or "weather" in user_input_lower:
            # 提取城市
            cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", 
                     "西安", "天津", "重庆", "苏州", "长沙", "郑州", "青岛", "大连"]
            location = "北京"
            for city in cities:
                if city in user_input:
                    location = city
                    break
            
            days = 7
            if any(kw in user_input_lower for kw in ["现在", "今天", "当前"]):
                days = 1
            
            return json.dumps({
                "tool": "weather",
                "parameters": {"location": location, "days": days},
                "reasoning": "用户查询天气信息"
            })
        elif "股票" in user_input_lower:
            return json.dumps({
                "tool": "stock",
                "parameters": {"symbol": "000001", "days": 5},
                "reasoning": "用户查询股票信息"
            })
        elif "计算" in user_input_lower or "+" in user_input or "-" in user_input:
            return json.dumps({
                "tool": "calculate",
                "parameters": {"expression": user_input},
                "reasoning": "用户需要进行计算"
            })
        else:
            return json.dumps({
                "tool": None,
                "reasoning": "无法识别用户意图，使用默认处理"
            })

