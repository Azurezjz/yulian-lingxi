"""
Agent 调度逻辑
"""
from typing import Dict, Any, Optional
import json
import re
from app.core.scheduler import ToolScheduler
from app.core.prompt import PromptTemplate
from app.core.llm_service import LLMService

class Agent:
    """智能 Agent，负责意图识别和工具调度"""
    
    def __init__(self):
        self.scheduler = ToolScheduler()
        self.prompt_template = PromptTemplate()
        self.llm_service = LLMService()
        self._last_user_input = ""  # 保存最后一次用户输入，用于降级方案
    
    async def execute(
        self, 
        user_input: str, 
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行用户请求（支持多工具链式调用）
        
        Args:
            user_input: 用户输入的自然语言
            conversation_id: 对话 ID（用于多轮对话）
            
        Returns:
            工作流执行结果，格式：
            {
                "intent_type": "weather" | "news" | "stock" | "calculate" | "document" | "data",
                "tool_name": "工具名称" | ["工具1", "工具2", ...],  # 多工具时返回列表
                "tool_params": {...} | [{...}, {...}, ...],  # 多工具时返回列表
                "tool_result": {...} | [{...}, {...}, ...],  # 多工具时返回列表
                "is_multi_tool": True/False,  # 是否是多工具调用
                "tool_chain": [...]  # 工具链信息
            }
        """
        try:
            # 保存原始用户输入，用于降级方案
            self._last_user_input = user_input
            
            # 检查是否包含多个任务（简单检测）
            has_multiple_tasks = self._detect_multiple_tasks(user_input)
            if has_multiple_tasks:
                print(f"[DEBUG] Agent 检测到多任务请求，将尝试识别所有任务")
            
            # 1. 使用大模型进行意图识别和参数提取
            intent_result = await self._recognize_intent(user_input)
            
            # 2. 解析大模型返回的结果（支持多工具）
            parsed_result = self._parse_intent_result(intent_result, user_input)
            
            # 检查是否是多工具调用
            if isinstance(parsed_result, dict) and "tools" in parsed_result:
                # 多工具链式调用
                tools_list = parsed_result["tools"]
                print(f"[DEBUG] Agent 识别到 {len(tools_list)} 个工具，开始链式调用")
                
                tool_chain = []
                all_results = []
                previous_result = None
                
                for i, tool_info in enumerate(tools_list):
                    tool_name = tool_info.get("tool")
                    tool_params = tool_info.get("parameters", {})
                    
                    print(f"[DEBUG] Agent 执行工具 {i+1}/{len(tools_list)}: {tool_name}")
                    
                    # 如果当前工具是 document，且前面有工具结果，将结果作为上下文数据
                    if tool_name == "document" and previous_result:
                        # 将前一个工具的结果整合到 document 工具的 data 参数中
                        if previous_result.get("success") and previous_result.get("data"):
                            tool_params["data"] = previous_result["data"]
                            # 更新 content，包含对前一个工具结果的引用
                            if "content" in tool_params:
                                tool_params["content"] = f"{tool_params['content']}（基于前一个工具的执行结果）"
                            else:
                                tool_params["content"] = "基于前一个工具的执行结果生成总结"
                    
                    # 调用工具
                    tool_result = await self.scheduler.call_tool(tool_name, tool_params)
                    
                    # 记录工具链信息
                    tool_chain.append({
                        "step": i + 1,
                        "tool_name": tool_name,
                        "tool_params": tool_params,
                        "success": tool_result.get("success", False)
                    })
                    
                    all_results.append({
                        "tool_name": tool_name,
                        "tool_params": tool_params,
                        "tool_result": tool_result
                    })
                    
                    previous_result = tool_result
                    
                    # 如果某个工具失败，可以选择继续或停止
                    if not tool_result.get("success"):
                        print(f"[WARNING] 工具 {tool_name} 执行失败，但继续执行后续工具")
                
                # 返回多工具结果
                return {
                    "intent_type": tools_list[0].get("tool") if tools_list else "data",
                    "tool_name": [t.get("tool") for t in tools_list],
                    "tool_params": [t.get("parameters", {}) for t in tools_list],
                    "tool_result": all_results,
                    "is_multi_tool": True,
                    "tool_chain": tool_chain
                }
            else:
                # 单工具调用（原有逻辑）
                tool_name, tool_params = parsed_result
                
                # 3. 如果检测到多任务但大模型只识别了一个，尝试提取其他任务
                if has_multiple_tasks and tool_name:
                    additional_tool = self._extract_additional_tool(user_input, tool_name)
                    if additional_tool:
                        print(f"[DEBUG] Agent 检测到额外任务: {additional_tool['tool_name']}")
                        # 如果主要工具不是计算，但检测到计算任务，优先执行计算
                        if additional_tool["tool_name"] == "calculate" and tool_name != "calculate":
                            print(f"[DEBUG] Agent 优先执行计算任务")
                            tool_name = "calculate"
                            tool_params = additional_tool["tool_params"]
                
                # 调试信息
                print(f"[DEBUG] Agent 解析结果 - tool_name: {tool_name}, tool_params: {tool_params}")
                
                # 4. 调用工具
                tool_result = None
                if tool_name:
                    tool_result = await self.scheduler.call_tool(tool_name, tool_params)
                
                # 5. 返回结果
                return {
                    "intent_type": tool_name if tool_name else "data",
                    "tool_name": tool_name if tool_name else "unknown",
                    "tool_params": tool_params,
                    "tool_result": tool_result,
                    "is_multi_tool": False,
                    "tool_chain": []
                }
        except Exception as e:
            print(f"Agent 执行失败：{e}")
            import traceback
            print(f"错误详情：{traceback.format_exc()}")
            # 返回错误结果
            return {
                "intent_type": "data",
                "tool_name": "error",
                "tool_params": {},
                "tool_result": {
                    "success": False,
                    "error": str(e),
                    "data": None
                },
                "is_multi_tool": False,
                "tool_chain": []
            }
    
    def _detect_multiple_tasks(self, user_input: str) -> bool:
        """检测用户输入是否包含多个任务"""
        # 检测关键词组合
        task_keywords = {
            "weather": ["天气", "气温", "温度", "weather"],
            "calculate": ["计算", "算", "等于", "+", "-", "*", "/", "加", "减", "乘", "除"],
            "news": ["新闻", "资讯", "news"],
            "stock": ["股票", "stock"]
        }
        
        detected_tasks = []
        user_input_lower = user_input.lower()
        
        for task_type, keywords in task_keywords.items():
            if any(kw in user_input_lower for kw in keywords):
                detected_tasks.append(task_type)
        
        return len(detected_tasks) > 1
    
    def _extract_additional_tool(self, user_input: str, current_tool: str) -> Optional[Dict[str, Any]]:
        """从用户输入中提取额外的工具需求"""
        user_input_lower = user_input.lower()
        
        # 如果当前工具不是计算，但用户输入包含计算表达式
        if current_tool != "calculate":
            # 检测计算表达式
            calc_patterns = [
                r'计算\s*([+\-*/0-9\s.()]+)',
                r'算\s*([+\-*/0-9\s.()]+)',
                r'([0-9]+\s*[+\-*/]\s*[0-9]+)',
                r'等于\s*([+\-*/0-9\s.()]+)'
            ]
            
            for pattern in calc_patterns:
                match = re.search(pattern, user_input)
                if match:
                    expression = match.group(1) if match.groups() else match.group(0)
                    expression = expression.strip()
                    # 清理表达式
                    expression = re.sub(r'\s+', '', expression)
                    if expression:
                        return {
                            "tool_name": "calculate",
                            "tool_params": {"expression": expression}
                        }
        
        return None
    
    async def _recognize_intent(self, user_input: str) -> str:
        """
        使用大模型识别用户意图
        
        Returns:
            JSON 格式的意图识别结果
        """
        # 构建提示词
        prompt = self.prompt_template.get_intent_recognition_prompt(user_input)
        
        # 调用大模型
        messages = [
            {
                "role": "system",
                "content": "你是一个智能助手，负责分析用户需求并选择合适的工具。请严格按照 JSON 格式返回结果。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        print(f"[DEBUG] Agent 调用大模型 - 用户输入: {user_input}")
        response = await self.llm_service.chat(messages, temperature=0.3, user_input=user_input)
        print(f"[DEBUG] Agent 收到大模型响应 - 长度: {len(response)} 字符")
        print(f"[DEBUG] Agent 收到大模型响应 - 内容: {response[:300]}...")
        return response
    
    def _parse_intent_result(self, intent_result: str, user_input: str):
        """
        解析大模型返回的意图识别结果（支持单工具和多工具）
        
        Returns:
            单工具: (tool_name, tool_params) 元组
            多工具: {"tools": [...]} 字典
        """
        try:
            # 尝试解析 JSON
            # 处理可能的 markdown 代码块
            intent_result = intent_result.strip()
            print(f"[DEBUG] Agent 解析 - 原始响应: {intent_result[:200]}...")
            
            if "```json" in intent_result:
                match = re.search(r'```json\s*(.*?)\s*```', intent_result, re.DOTALL)
                if match:
                    intent_result = match.group(1)
                    print(f"[DEBUG] Agent 解析 - 从 markdown 代码块中提取 JSON")
            elif "```" in intent_result:
                match = re.search(r'```\s*(.*?)\s*```', intent_result, re.DOTALL)
                if match:
                    intent_result = match.group(1)
                    print(f"[DEBUG] Agent 解析 - 从代码块中提取内容")
            
            # 尝试提取 JSON 对象（支持多工具格式）
            # 先尝试匹配多工具格式（包含 "tools" 数组）
            multi_tool_match = re.search(r'\{[^{}]*"tools"[^{}]*\[[^\]]*\][^{}]*\}', intent_result, re.DOTALL)
            if multi_tool_match:
                intent_result = multi_tool_match.group(0)
                print(f"[DEBUG] Agent 解析 - 从文本中提取多工具 JSON 对象")
            else:
                # 尝试匹配单工具格式
                single_tool_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', intent_result, re.DOTALL)
                if single_tool_match:
                    intent_result = single_tool_match.group(0)
                    print(f"[DEBUG] Agent 解析 - 从文本中提取单工具 JSON 对象")
            
            result = json.loads(intent_result)
            print(f"[DEBUG] Agent 解析 - JSON 解析成功: {result}")
            
            # 检查是否是多工具格式
            if "tools" in result and isinstance(result["tools"], list):
                # 多工具格式
                tools_list = result["tools"]
                print(f"[DEBUG] Agent 解析 - 识别到 {len(tools_list)} 个工具")
                
                # 处理每个工具的参数
                processed_tools = []
                for tool_info in tools_list:
                    tool_name = tool_info.get("tool", "").lower()
                    parameters = tool_info.get("parameters", {})
                    
                    # 参数后处理
                    processed_params = self._process_tool_params(tool_name, parameters, user_input)
                    processed_tools.append({
                        "tool": tool_name,
                        "parameters": processed_params
                    })
                
                return {"tools": processed_tools}
            
            # 单工具格式
            tool_name = result.get("tool")
            if not tool_name:
                print(f"[DEBUG] Agent 解析 - 未找到 tool 字段，降级到规则识别")
                return self._fallback_parse(user_input)
            
            # 转换为小写，匹配工具注册表中的名称
            tool_name = tool_name.lower()
            print(f"[DEBUG] Agent 解析 - 识别工具: {tool_name}")
            
            # 提取参数
            parameters = result.get("parameters", {})
            print(f"[DEBUG] Agent 解析 - 提取参数: {parameters}")
            
            # 参数后处理
            processed_params = self._process_tool_params(tool_name, parameters, user_input)
            
            return tool_name, processed_params
                
        except json.JSONDecodeError as e:
            print(f"[ERROR] Agent JSON 解析失败：{e}")
            print(f"[ERROR] Agent 原始结果：{intent_result[:500]}")
            print(f"[ERROR] Agent 降级到规则识别")
            # 降级到规则识别
            return self._fallback_parse(user_input)
        except Exception as e:
            print(f"[ERROR] Agent 解析意图结果失败：{e}")
            import traceback
            print(f"[ERROR] 错误详情：{traceback.format_exc()}")
            return self._fallback_parse(user_input)
    
    def _process_tool_params(self, tool_name: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """处理工具参数（统一的后处理逻辑）"""
        if tool_name == "weather":
            location = parameters.get("location", "北京")
            days = parameters.get("days", 7)
            # 如果参数中没有城市，尝试从用户输入中提取
            if not location or location == "未知":
                location = self._extract_city(user_input)
            print(f"[DEBUG] Agent 解析 - 天气工具: location={location}, days={days}")
            return {"location": location, "days": days}
        
        elif tool_name == "news":
            query = parameters.get("query", user_input)
            limit = parameters.get("limit", 10)
            print(f"[DEBUG] Agent 解析 - 新闻工具: query={query}, limit={limit}")
            return {"query": query, "limit": limit}
        
        elif tool_name == "stock":
            symbol = parameters.get("symbol", "000001")
            days = parameters.get("days", 5)
            
            # 股票名称到代码的映射
            stock_name_to_code = {
                "贵州茅台": "600519",
                "茅台": "600519",
                "平安银行": "000001",
                "平安": "000001",
                "腾讯控股": "00700",
                "腾讯": "00700",
                "阿里巴巴": "09988",
                "阿里": "09988",
                "万科A": "000002",
                "万科": "000002",
                "招商银行": "600036",
                "五粮液": "000858",
            }
            
            # 如果 symbol 是股票名称，转换为代码
            original_symbol = symbol
            if symbol in stock_name_to_code:
                symbol = stock_name_to_code[symbol]
                print(f"[DEBUG] Agent 股票名称转换: {original_symbol} -> {symbol}")
            
            print(f"[DEBUG] Agent 解析 - 股票工具: symbol={symbol}, days={days}")
            return {"symbol": symbol, "days": days}
        
        elif tool_name == "calculate":
            expression = parameters.get("expression", user_input)
            print(f"[DEBUG] Agent 解析 - 计算工具: expression={expression}")
            return {"expression": expression}
        
        elif tool_name == "document":
            template = parameters.get("template", "summary")  # 默认 summary
            content = parameters.get("content", user_input)
            data = parameters.get("data", {})  # 保留 data 参数（可能来自前一个工具）
            print(f"[DEBUG] Agent 解析 - 文档工具: template={template}, content={content[:50]}...")
            return {"template": template, "content": content, "data": data}
        
        else:
            return parameters
    
    def _extract_city(self, user_input: str) -> str:
        """从用户输入中提取城市名称"""
        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", 
                 "西安", "天津", "重庆", "苏州", "长沙", "郑州", "青岛", "大连",
                 "济南", "福州", "厦门", "合肥", "石家庄", "哈尔滨", "长春", "沈阳"]
        for city in cities:
            if city in user_input:
                return city
        return "北京"  # 默认
    
    def _fallback_parse(self, user_input: str) -> tuple:
        """降级方案：基于规则的解析"""
        print(f"[DEBUG] Agent 使用降级方案（规则识别）- 用户输入: {user_input}")
        user_input_lower = user_input.lower()
        
        # 按优先级检查（新闻优先，必须明确包含"新闻"或"资讯"）
        if "新闻" in user_input_lower or "资讯" in user_input_lower or "news" in user_input_lower:
            # 提取查询关键词
            query = user_input
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
                if "ai" in user_input_lower or "人工智能" in user_input_lower:
                    query = "AI"
                elif "科技" in user_input_lower:
                    query = "科技"
                elif "国内" in user_input_lower:
                    query = "国内"
                else:
                    query = "科技"
            
            return "news", {"query": query, "limit": limit}
        elif "天气" in user_input_lower or "气温" in user_input_lower:
            location = self._extract_city(user_input)
            days = 1 if any(kw in user_input_lower for kw in ["现在", "今天"]) else 7
            return "weather", {"location": location, "days": days}
        elif "股票" in user_input_lower:
            return "stock", {"symbol": "000001", "days": 5}
        elif "计算" in user_input_lower or "+" in user_input or "-" in user_input:
            return "calculate", {"expression": user_input}
        else:
            return None, {}

