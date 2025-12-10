"""
API 路由定义
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
import re
import json
from app.core.agent import Agent
from app.core.scheduler import ToolScheduler

router = APIRouter()
scheduler = ToolScheduler()

class WorkflowRequest(BaseModel):
    """工作流执行请求"""
    userInput: str
    conversationId: Optional[str] = None

@router.post("/workflow/execute")
async def execute_workflow(request: WorkflowRequest):
    """
    执行工作流
    
    接收用户自然语言输入，执行意图识别、工具调度、结果生成等完整流程。
    """
    import time
    from datetime import datetime
    
    try:
        task_id = str(int(time.time() * 1000))
        now = datetime.now().strftime("%H:%M:%S")
        
        # 使用 Agent 进行意图识别和工具调度
        agent = Agent()
        agent_result = await agent.execute(request.userInput, request.conversationId)
        
        # 从 Agent 结果中提取信息
        intent_type = agent_result.get("intent_type", "data")
        tool_name = agent_result.get("tool_name", "")
        tool_params = agent_result.get("tool_params", {})
        tool_result = agent_result.get("tool_result")
        is_multi_tool = agent_result.get("is_multi_tool", False)
        tool_chain = agent_result.get("tool_chain", [])
        
        # 调试信息（可以注释掉）
        print(f"[DEBUG] Agent 结果 - intent_type: {intent_type}, tool_name: {tool_name}, is_multi_tool: {is_multi_tool}")
        
        # 处理多工具链式调用
        original_tool_results = None
        if is_multi_tool and isinstance(tool_result, list):
            print(f"[DEBUG] 处理多工具链式调用，共 {len(tool_result)} 个工具")
            # 保存原始的工具结果列表（用于后续处理）
            original_tool_results = tool_result
            print(f"[DEBUG] 保存原始工具结果列表，长度: {len(original_tool_results)}")
            
            # 获取最后一个工具的结果（通常是最终结果）
            if tool_result:
                last_tool_exec = tool_result[-1]
                last_tool_name = last_tool_exec.get("tool_name", "")
                last_result = last_tool_exec.get("tool_result")
                
                # 更新 intent_type 为最后一个工具的类型
                if last_tool_name:
                    intent_type = last_tool_name
                
                if last_result and last_result.get("success"):
                    tool_result = last_result
                else:
                    # 如果最后一个工具失败，使用第一个工具的结果
                    if tool_result:
                        first_tool_exec = tool_result[0]
                        first_tool_name = first_tool_exec.get("tool_name", "")
                        first_result = first_tool_exec.get("tool_result")
                        if first_result:
                            tool_result = first_result
                            # 更新 intent_type 为第一个工具的类型
                            if first_tool_name:
                                intent_type = first_tool_name
        
        # 初始化变量（用于结果格式化）
        # 处理 tool_params 可能是列表的情况（多工具调用）
        if isinstance(tool_params, list):
            # 多工具调用时，从第一个工具的参数中提取信息（用于天气、新闻、股票等）
            if tool_params:
                first_params = tool_params[0]
                location = first_params.get("location", "北京")
                days = first_params.get("days", 7)
                query = first_params.get("query", "")
                limit = first_params.get("limit", 10)
                symbol = first_params.get("symbol", "000001")
                expression = first_params.get("expression", "")
                
                # 如果最后一个工具是 document，从最后一个工具的参数中提取 template 和 content
                if len(tool_params) > 1 and isinstance(tool_name, list) and len(tool_name) > 1:
                    last_tool_name = tool_name[-1] if isinstance(tool_name, list) else ""
                    if last_tool_name == "document":
                        last_params = tool_params[-1]
                        template = last_params.get("template", "report")
                        content = last_params.get("content", "")
                    else:
                        template = first_params.get("template", "report")
                        content = first_params.get("content", "")
                else:
                    template = first_params.get("template", "report")
                    content = first_params.get("content", "")
            else:
                # 如果列表为空，使用默认值
                location = "北京"
                days = 7
                query = ""
                limit = 10
                symbol = "000001"
                expression = ""
                template = "report"
                content = ""
        else:
            # 单工具调用，tool_params 是字典
            location = tool_params.get("location", "北京")
            days = tool_params.get("days", 7)
            query = tool_params.get("query", "")
            limit = tool_params.get("limit", 10)
            symbol = tool_params.get("symbol", "000001")
            expression = tool_params.get("expression", "")
            template = tool_params.get("template", "report")
            content = tool_params.get("content", "")
        
        user_input = request.userInput
        
        # 如果 tool_name 存在，使用 tool_name 作为 intent_type（更可靠）
        # 处理 tool_name 可能是列表的情况（多工具调用）
        if tool_name:
            if isinstance(tool_name, list):
                # 多工具调用时，使用最后一个工具的名称
                if tool_name:
                    intent_type = tool_name[-1]
            elif tool_name != "unknown" and tool_name != "error":
                intent_type = tool_name
        
        # 如果 Agent 成功返回工具结果，直接使用
        if tool_result and tool_result.get("success"):
            # Agent 已成功识别并调用工具，直接使用结果
            pass
        else:
            # Agent 失败或未识别，使用降级方案（基于规则的识别）
            user_input = request.userInput
            user_input_lower = user_input.lower()
            
            # 初始化变量
            intent_type = "data"
            location = "北京"
            days = 7
            query = ""
            limit = 10
            symbol = "000001"
            expression = ""
            template = "report"
            content = ""
            
            # 判断意图类型（降级方案，按优先级顺序）
            # 检查新闻相关关键词（必须明确包含"新闻"或"资讯"，避免误判天气查询）
            if "新闻" in user_input_lower or "资讯" in user_input_lower or "news" in user_input_lower:
                intent_type = "news"
                # 提取查询关键词
                query = user_input
                # 移除常见动词和名词
                query = re.sub(r'抓取|检索|搜索|找|看看|查|列出|总结|最近的', '', query)
                query = re.sub(r'新闻|资讯|news|条', '', query, flags=re.IGNORECASE)
                query = query.strip()
                
                # 提取领域关键词
                if not query or len(query) < 2:
                    if "ai" in user_input_lower or "人工智能" in user_input_lower:
                        query = "AI"
                    elif "科技" in user_input_lower:
                        query = "科技"
                    elif "国内" in user_input_lower:
                        query = "国内"
                    else:
                        query = "科技"  # 默认关键词
                
                # 提取数量
                limit = 10
                limit_match = re.search(r'(\d+)\s*条', user_input)
                if limit_match:
                    limit = int(limit_match.group(1))
                    limit = min(max(limit, 1), 50)  # 限制在1-50条
                
            elif "天气" in user_input_lower or "气温" in user_input_lower or "weather" in user_input_lower:
                intent_type = "weather"
                # 提取城市名称（支持更多城市）
                cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", 
                         "西安", "天津", "重庆", "苏州", "长沙", "郑州", "青岛", "大连",
                         "济南", "福州", "厦门", "合肥", "石家庄", "哈尔滨", "长春", "沈阳"]
                location = "北京"  # 默认值
                for city in cities:
                    if city in user_input:
                        location = city
                        break
                
                # 提取天数
                # 判断是否是"现在"、"今天"、"当前"等关键词
                if any(keyword in user_input_lower for keyword in ["现在", "今天", "当前", "今日"]):
                    days = 1
                else:
                    days = 7  # 默认7天
                    days_match = re.search(r'(\d+)\s*天', user_input)
                    if days_match:
                        days = int(days_match.group(1))
                        days = min(max(days, 1), 7)  # 限制在1-7天
                    
            elif "股票" in user_input_lower or "stock" in user_input_lower:
                intent_type = "stock"
                # 提取股票代码或名称
                symbol = "000001"  # 默认
                # 尝试提取股票代码（6位数字）
                symbol_match = re.search(r'(\d{6})', user_input)
                if symbol_match:
                    symbol = symbol_match.group(1)
                # 尝试提取股票名称
                stock_names = {"茅台": "600519", "平安": "000001", "腾讯": "00700", "阿里": "09988"}
                for name, code in stock_names.items():
                    if name in user_input:
                        symbol = code
                        break
                
                # 提取天数
                days = 5
                days_match = re.search(r'(\d+)\s*[日天]', user_input)
                if days_match:
                    days = int(days_match.group(1))
                    days = min(max(days, 1), 30)  # 限制在1-30天
                    
            elif "计算" in user_input_lower or "算" in user_input_lower or "+" in user_input or "-" in user_input or "*" in user_input:
                intent_type = "calculate"
                # 提取计算表达式
                expression = user_input
                # 移除"计算"、"算"等词
                expression = re.sub(r'计算|算|等于|是多少', '', expression)
                expression = expression.strip()
                
            elif "生成" in user_input_lower or "写" in user_input_lower or "文档" in user_input_lower:
                intent_type = "document"
                # 提取模板类型和内容
                template = "report"
                if "报告" in user_input_lower:
                    template = "report"
                elif "邮件" in user_input_lower or "email" in user_input_lower:
                    template = "email"
                elif "总结" in user_input_lower or "摘要" in user_input_lower:
                    template = "summary"
                
                content = user_input
                # 移除"生成"、"写"等词
                content = re.sub(r'生成|写|创建|制作', '', content)
                content = content.strip()
                
            else:
                intent_type = "data"
        
        # 构建工作流步骤
        if is_multi_tool and tool_chain:
            # 多工具链式调用，为每个工具创建步骤
            steps = [
                {
                    "id": "1",
                    "name": "意图识别",
                    "description": "分析用户自然语言需求（识别到多个工具）",
                    "status": "success",
                    "timestamp": now
                }
            ]
            # 为每个工具添加步骤
            for i, tool_info in enumerate(tool_chain, 2):
                steps.append({
                    "id": str(i),
                    "name": f"执行工具 {i-1}",
                    "description": f"调用 {tool_info['tool_name']} 工具",
                    "status": "success" if tool_info.get("success") else "failed",
                    "timestamp": now
                })
            steps.append({
                "id": str(len(tool_chain) + 2),
                "name": "结果整合",
                "description": "整合所有工具的执行结果",
                "status": "success",
                "timestamp": now
            })
        else:
            # 单工具调用
            steps = [
                {
                    "id": "1",
                    "name": "意图识别",
                    "description": "分析用户自然语言需求",
                    "status": "success",
                    "timestamp": now
                },
                {
                    "id": "2",
                    "name": "工具路由",
                    "description": "选择合适的工具链",
                    "status": "success",
                    "timestamp": now
                },
                {
                    "id": "3",
                    "name": "执行调用",
                    "description": "与外部 API 进行交互",
                    "status": "success",
                    "timestamp": now
                },
                {
                    "id": "4",
                    "name": "结果生成",
                    "description": "整合数据并生成可视化报告",
                    "status": "success",
                    "timestamp": now
                }
            ]
        
        # 构建工具调用日志
        logs = [
            {
                "id": "log-1",
                "toolName": "Orchestrator",
                "inputParams": f'{{"intent": "{intent_type}", "is_multi_tool": {is_multi_tool}, "confidence": 0.95}}',
                "outputResult": '{"status": 200}',
                "status": "success",
                "duration": "120ms",
                "timestamp": now
            }
        ]
        
        # 如果是多工具调用，为每个工具添加日志
        if is_multi_tool and isinstance(agent_result.get("tool_result"), list):
            for i, tool_exec in enumerate(agent_result["tool_result"], 2):
                tool_name = tool_exec.get("tool_name", "unknown")
                tool_params = tool_exec.get("tool_params", {})
                tool_res = tool_exec.get("tool_result", {})
                tool_status = "success" if tool_res.get("success") else "failed"
                tool_duration = tool_res.get("metadata", {}).get("duration", "0ms") if tool_res else "0ms"
                
                logs.append({
                    "id": f"log-{i}",
                    "toolName": tool_name.upper(),
                    "inputParams": json.dumps(tool_params, ensure_ascii=False),
                    "outputResult": json.dumps({"status": 200 if tool_status == "success" else 500}),
                    "status": tool_status,
                    "duration": tool_duration,
                    "timestamp": now
                })
        
        # 如果 Agent 没有返回工具结果，才调用工具（降级方案）
        if not tool_result or not tool_result.get("success"):
            # 根据意图类型调用相应的工具
            if intent_type == "weather":
                tool_name = "weather"
                tool_params = {"location": location, "days": days}
                tool_result = await scheduler.call_tool("weather", tool_params)
                
            elif intent_type == "news":
                tool_name = "news"
                tool_params = {"query": query, "limit": limit}
                tool_result = await scheduler.call_tool("news", tool_params)
                
            elif intent_type == "stock":
                tool_name = "stock"
                tool_params = {"symbol": symbol, "days": days}
                tool_result = await scheduler.call_tool("stock", tool_params)
                
            elif intent_type == "calculate":
                tool_name = "calculate"
                tool_params = {"expression": expression}
                tool_result = await scheduler.call_tool("calculate", tool_params)
                
            elif intent_type == "document":
                tool_name = "document"
                tool_params = {"template": template, "content": content}
                tool_result = await scheduler.call_tool("document", tool_params)
                
            else:
                # 未识别的意图，返回友好的提示
                tool_name = "Unknown Intent"
                tool_params = {"userInput": user_input}
                tool_result = {
                    "success": True,
                    "data": {
                        "summary": f"抱歉，我暂时无法理解您的需求：\"{user_input}\"。\n\n我可以帮您：\n- 查询天气（如：查北京天气）\n- 检索新闻（如：查AI新闻）\n- 查询股票（如：查贵州茅台股票）\n- 进行计算（如：计算 2+3）\n- 生成文档（如：写一份报告）",
                        "chartType": "none",
                        "chartData": [],
                        "rawData": []
                    }
                }
        
        # 处理工具返回结果，转换为前端需要的格式
        # 初始化 result 变量
        result = None
        
        # 如果是多工具调用，需要合并所有工具的结果
        if is_multi_tool and original_tool_results:
            print(f"[DEBUG] 处理多工具结果合并，共 {len(original_tool_results)} 个工具")
            
            # 获取第一个工具的结果（用于显示图表）
            first_tool_exec = original_tool_results[0]
            first_tool_name = first_tool_exec.get("tool_name", "")
            first_tool_result = first_tool_exec.get("tool_result", {})
            first_tool_data = first_tool_result.get("data", {}) if first_tool_result.get("success") else {}
            
            # 获取最后一个工具的结果（通常是文档总结）
            last_tool_exec = original_tool_results[-1]
            last_tool_name = last_tool_exec.get("tool_name", "")
            last_tool_result = last_tool_exec.get("tool_result", {})
            last_tool_data = last_tool_result.get("data", {}) if last_tool_result.get("success") else {}
            
            # 合并结果：第一个工具的数据 + 最后一个工具的数据
            if first_tool_name == "weather" and first_tool_result.get("success"):
                # 处理天气数据（用于图表）
                forecast = first_tool_data.get("forecast", [])
                chart_data = [
                    {
                        "name": item["date"],
                        "temperature": item["maxTemp"],
                        "humidity": item["humidity"]
                    }
                    for item in forecast
                ]
                
                # 如果有股票结果，合并到摘要中
                if last_tool_name == "stock" and last_tool_result.get("success"):
                    stock_data = last_tool_data
                    stock_symbol = stock_data.get("symbol", "")
                    stock_name = stock_data.get("name", "")
                    stock_prices = stock_data.get("prices", [])
                    
                    # 合并天气和股票数据到摘要
                    weather_summary = f"已查询{location}未来{days}天天气情况。"
                    stock_summary = f"已查询{stock_name}({stock_symbol})股票数据，共 {len(stock_prices)} 天。"
                    
                    # 合并图表数据（天气温度 + 股票收盘价）
                    combined_chart_data = []
                    # 使用天气数据作为基础
                    for item in chart_data:
                        combined_chart_data.append({
                            "name": item["name"],
                            "temperature": item["temperature"],
                            "humidity": item["humidity"]
                        })
                    
                    # 构建详细的摘要信息
                    weather_details = "\n".join([f"- {item['date']}: {item['weather']}, 温度 {item['minTemp']}°C - {item['maxTemp']}°C" for item in forecast[:3]])
                    stock_details = "\n".join([f"- {item['date']}: 收盘价 {item['close']}, 成交量 {item['volume']}" for item in stock_prices[:3]])
                    
                    # 生成股票图表数据
                    stock_chart_data = [
                        {
                            "name": item["date"],
                            "close": item["close"],
                            "volume": item["volume"]
                        }
                        for item in stock_prices
                    ]
                    
                    # 返回包含多个工具数据的结构
                    # rawData 包含两个工具的数据，每个工具都有自己的图表数据
                    result = {
                        "summary": f"{weather_summary}\n\n{stock_summary}",
                        "chartType": "line",
                        "chartData": chart_data,  # 显示第一个工具（天气）的图表
                        "rawData": [
                            {
                                "type": "weather",
                                "title": f"{location}天气数据",
                                "data": forecast,
                                "chartType": "line",
                                "chartData": chart_data  # 天气图表数据
                            },
                            {
                                "type": "stock",
                                "title": f"{stock_name}({stock_symbol})股票数据",
                                "data": stock_prices,
                                "chartType": "line",
                                "chartData": stock_chart_data  # 股票图表数据
                            }
                        ]
                    }
                # 如果有文档结果，合并到摘要中
                elif last_tool_name == "document" and last_tool_result.get("success"):
                    doc_content = last_tool_data.get("content", "")
                    # rawData 返回天气数据数组（前端期望的格式）
                    # 文档内容已经在 summary 中包含了
                    result = {
                        "summary": f"已查询{location}未来{days}天天气情况，并生成了出行指南。\n\n## 天气数据\n\n根据气象工具查询，{location}未来{days}天天气情况如下：\n\n## 出行指南\n\n{doc_content}",
                        "chartType": "line",
                        "chartData": chart_data,
                        "rawData": forecast  # 返回天气数据数组，符合前端期望
                    }
                else:
                    # 只有天气数据
                    result = {
                        "summary": f"根据气象工具查询，{location}未来{days}天天气情况如下：气温呈波动趋势，建议关注天气变化，合理安排出行。",
                        "chartType": "line",
                        "chartData": chart_data,
                        "rawData": forecast
                    }
                    
            elif first_tool_name == "news" and first_tool_result.get("success"):
                # 处理新闻数据
                articles = first_tool_data.get("articles", [])
                
                # 如果有股票结果，合并到摘要中
                if last_tool_name == "stock" and last_tool_result.get("success"):
                    stock_data = last_tool_data
                    stock_symbol = stock_data.get("symbol", "")
                    stock_name = stock_data.get("name", "")
                    stock_prices = stock_data.get("prices", [])
                    
                    # 生成股票图表数据
                    stock_chart_data = [
                        {
                            "name": item["date"],
                            "close": item["close"],
                            "volume": item["volume"]
                        }
                        for item in stock_prices
                    ]
                    
                    result = {
                        "summary": f"已抓取到最近 {len(articles)} 条关于 '{query}' 的新闻。\n\n已查询{stock_name}({stock_symbol})股票数据，共 {len(stock_prices)} 天。",
                        "chartType": "line",
                        "chartData": stock_chart_data,  # 显示股票图表
                        "rawData": [
                            {
                                "type": "news",
                                "title": f"新闻数据（{query}）",
                                "data": articles,
                                "chartType": "none",
                                "chartData": []
                            },
                            {
                                "type": "stock",
                                "title": f"{stock_name}({stock_symbol})股票数据",
                                "data": stock_prices,
                                "chartType": "line",
                                "chartData": stock_chart_data  # 股票图表数据
                            }
                        ]
                    }
                # 如果有文档结果，合并到摘要中
                elif last_tool_name == "document" and last_tool_result.get("success"):
                    doc_content = last_tool_data.get("content", "")
                    # rawData 返回新闻文章数组（前端期望的格式）
                    # 文档内容已经在 summary 中包含了
                    result = {
                        "summary": f"已抓取到最近 {len(articles)} 条关于 '{query}' 的新闻，并生成了总结。\n\n## 新闻总结\n\n{doc_content}",
                        "chartType": "none",
                        "chartData": [],
                        "rawData": articles  # 返回新闻文章数组，符合前端期望
                    }
                else:
                    result = {
                        "summary": f"为您抓取到最近 {len(articles)} 条关于 '{query}' 的新闻。",
                        "chartType": "none",
                        "chartData": [],
                        "rawData": articles
                    }
                    
            elif first_tool_name == "stock" and first_tool_result.get("success"):
                # 处理股票数据
                prices = first_tool_data.get("prices", [])
                stock_symbol = first_tool_data.get("symbol", symbol)
                stock_name = first_tool_data.get("name", "")
                chart_data = [
                    {
                        "name": item["date"],
                        "close": item["close"],
                        "volume": item["volume"]
                    }
                    for item in prices
                ]
                
                # 如果有天气结果，合并到摘要中
                if last_tool_name == "weather" and last_tool_result.get("success"):
                    weather_data = last_tool_data
                    weather_location = weather_data.get("location", location)
                    weather_forecast = weather_data.get("forecast", [])
                    
                    # 生成天气图表数据
                    weather_chart_data = [
                        {
                            "name": item["date"],
                            "temperature": item["maxTemp"],
                            "humidity": item["humidity"]
                        }
                        for item in weather_forecast
                    ]
                    
                    result = {
                        "summary": f"已查询{stock_name}({stock_symbol})股票数据，共 {len(prices)} 天。\n\n已查询{weather_location}未来{len(weather_forecast)}天天气情况。",
                        "chartType": "line",
                        "chartData": chart_data,  # 显示第一个工具（股票）的图表
                        "rawData": [
                            {
                                "type": "stock",
                                "title": f"{stock_name}({stock_symbol})股票数据",
                                "data": prices,
                                "chartType": "line",
                                "chartData": chart_data  # 股票图表数据
                            },
                            {
                                "type": "weather",
                                "title": f"{weather_location}天气数据",
                                "data": weather_forecast,
                                "chartType": "line",
                                "chartData": weather_chart_data  # 天气图表数据
                            }
                        ]
                    }
                # 如果有文档结果，合并到摘要中
                elif last_tool_name == "document" and last_tool_result.get("success"):
                    doc_content = last_tool_data.get("content", "")
                    # rawData 返回股票数据数组（前端期望的格式）
                    # 文档内容已经在 summary 中包含了
                    result = {
                        "summary": f"已查询股票数据，并生成了分析报告。\n\n## 股票分析\n\n{doc_content}",
                        "chartType": "line",
                        "chartData": chart_data,
                        "rawData": prices  # 返回股票数据数组，符合前端期望
                    }
                else:
                    result = {
                        "summary": f"股票 {stock_symbol} ({stock_name}) 近{days}日数据已查询。",
                        "chartType": "line",
                        "chartData": chart_data,
                        "rawData": prices
                    }
            else:
                # 其他情况，使用最后一个工具的结果
                if last_tool_result.get("success"):
                    tool_data = last_tool_data
                    if "content" in tool_data and "format" in tool_data:
                        doc_content = tool_data.get("content", "")
                        template_type = tool_data.get("template", template)
                        result = {
                            "summary": f"已完成多工具链式调用，最终生成了{template_type}文档，共 {tool_data.get('word_count', 0)} 字。\n\n文档内容：\n{doc_content}",
                            "chartType": "none",
                            "chartData": [],
                            "rawData": [{"content": doc_content, "format": tool_data.get("format", "markdown"), "template": template_type}]
                        }
                    else:
                        result = {
                            "summary": "多工具调用完成",
                            "chartType": "none",
                            "chartData": [],
                            "rawData": []
                        }
                else:
                    result = {
                        "summary": "多工具调用失败",
                        "chartType": "none",
                        "chartData": [],
                        "rawData": []
                    }
        elif tool_result and tool_result.get("success"):
            tool_data = tool_result["data"]
            
            # 根据 tool_name 确定 intent_type（最可靠的方式）
            # 优先使用 tool_name，因为它直接来自工具调用
            if tool_name and tool_name not in ["unknown", "error", "Unknown Intent", ""]:
                if isinstance(tool_name, list):
                    intent_type = tool_name[-1] if tool_name else "data"
                else:
                    intent_type = tool_name
            # 如果 tool_name 不可用，根据 tool_data 的结构判断
            elif tool_data:
                if "forecast" in tool_data:
                    intent_type = "weather"
                elif "articles" in tool_data:
                    intent_type = "news"
                elif "prices" in tool_data:
                    intent_type = "stock"
                elif "result" in tool_data and "expression" in tool_data:
                    intent_type = "calculate"
                elif "content" in tool_data and "format" in tool_data:
                    intent_type = "document"
            
            # 调试信息
            print(f"[DEBUG] 结果处理 - intent_type: {intent_type}, tool_name: {tool_name}, tool_data keys: {list(tool_data.keys()) if tool_data else 'None'}")
            
            if intent_type == "weather":
                # 转换天气数据格式
                forecast = tool_data.get("forecast", [])
                chart_data = [
                    {
                        "name": item["date"],
                        "temperature": item["maxTemp"],
                        "humidity": item["humidity"]
                    }
                    for item in forecast
                ]
                result = {
                    "summary": f"根据气象工具查询，{location}未来{days}天天气情况如下：气温呈波动趋势，建议关注天气变化，合理安排出行。",
                    "chartType": "line",
                    "chartData": chart_data,
                    "rawData": forecast
                }
                
            elif intent_type == "news":
                # 转换新闻数据格式
                articles = tool_data.get("articles", [])
                result = {
                    "summary": f"为您抓取到最近 {len(articles)} 条关于 '{query}' 的新闻。",
                    "chartType": "none",
                    "chartData": [],
                    "rawData": articles
                }
                
            elif intent_type == "stock":
                # 转换股票数据格式
                prices = tool_data.get("prices", [])
                chart_data = [
                    {
                        "name": item["date"],
                        "close": item["close"],
                        "volume": item["volume"]
                    }
                    for item in prices
                ]
                result = {
                    "summary": f"股票 {tool_data.get('symbol', symbol)} ({tool_data.get('name', '')}) 近{days}日数据已查询。",
                    "chartType": "line",
                    "chartData": chart_data,
                    "rawData": prices
                }
                
            elif intent_type == "calculate":
                # 转换计算数据格式
                calc_result = tool_data.get("result", 0)
                result = {
                    "summary": f"计算结果：{expression} = {calc_result}",
                    "chartType": "none",
                    "chartData": [],
                    "rawData": [{"expression": expression, "result": calc_result}]
                }
                
            elif intent_type == "document":
                # 转换文档数据格式
                doc_content = tool_data.get("content", "")
                template_type = tool_data.get("template", template)
                
                # 如果是多工具链式调用的结果，更新摘要
                if is_multi_tool:
                    result = {
                        "summary": f"已完成多工具链式调用，最终生成了{template_type}文档，共 {tool_data.get('word_count', 0)} 字。\n\n文档内容：\n{doc_content}",
                        "chartType": "none",
                        "chartData": [],
                        "rawData": [{"content": doc_content, "format": tool_data.get("format", "markdown"), "template": template_type}]
                    }
                else:
                    result = {
                        "summary": f"已生成{template_type}文档，共 {tool_data.get('word_count', 0)} 字。\n\n文档内容：\n{doc_content}",
                        "chartType": "none",
                        "chartData": [],
                        "rawData": [{"content": doc_content, "format": tool_data.get("format", "markdown")}]
                    }
                
            else:
                # 默认结果（未识别的意图或其他情况）
                result = {
                    "summary": tool_data.get("summary", "数据处理完成"),
                    "chartType": tool_data.get("chartType", "none"),
                    "chartData": tool_data.get("chartData", []),
                    "rawData": tool_data.get("rawData", [])
                }
        else:
            # 工具调用失败，返回错误信息
            error_msg = tool_result.get("error", "工具调用失败") if tool_result else "未知错误"
            result = {
                "summary": f"执行失败：{error_msg}",
                "chartType": "none",
                "chartData": [],
                "rawData": []
            }
        
        # 确保 result 已定义
        if result is None:
            print(f"[WARNING] result 未定义，使用默认值")
            result = {
                "summary": "处理结果时出现错误",
                "chartType": "none",
                "chartData": [],
                "rawData": []
            }
        
        # 调试信息：打印最终结果
        print(f"[DEBUG] 最终返回结果 - summary长度: {len(result.get('summary', ''))}, chartType: {result.get('chartType')}, chartData长度: {len(result.get('chartData', []))}, rawData类型: {type(result.get('rawData'))}")
        
        # 添加工具调用日志（如果不是多工具调用，才添加单个工具日志）
        if not is_multi_tool:
            tool_status = "success" if tool_result and tool_result.get("success") else "failed"
            tool_duration = tool_result.get("metadata", {}).get("duration", "850ms") if tool_result else "0ms"
            tool_output = json.dumps({"status": 200 if tool_status == "success" else 500}) if tool_result else '{"status": 500}'
            
            # 处理 tool_name 可能是列表的情况
            if isinstance(tool_name, list):
                tool_name_str = tool_name[0] if tool_name else "Unknown Tool"
            else:
                tool_name_str = tool_name if tool_name else "Unknown Tool"
            
            # 处理 tool_params 可能是列表的情况
            if isinstance(tool_params, list):
                tool_params_dict = tool_params[0] if tool_params else {}
            else:
                tool_params_dict = tool_params
            
            logs.append({
                "id": "log-2",
                "toolName": tool_name_str.upper() if isinstance(tool_name_str, str) else "Unknown Tool",
                "inputParams": json.dumps(tool_params_dict, ensure_ascii=False),
                "outputResult": tool_output,
                "status": tool_status,
                "duration": tool_duration,
                "timestamp": now
            })
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "taskId": task_id,
                "status": "success",
                "steps": steps,
                "logs": logs,
                "result": result
            }
        }
    except asyncio.CancelledError:
        # 正确处理取消操作
        raise HTTPException(
            status_code=503,
            detail="请求被取消"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"工作流执行失败：{str(e)}"
        )

@router.get("/tools/status")
async def get_tools_status():
    """
    查询工具状态
    """
    # TODO: 实现工具状态查询
    return {
        "code": 200,
        "message": "success",
        "data": {
            "tools": [
                {
                    "name": "Weather API",
                    "status": "available",
                    "description": "天气查询工具，支持7天预报"
                },
                {
                    "name": "News API",
                    "status": "available",
                    "description": "新闻检索工具"
                },
                {
                    "name": "Stock API",
                    "status": "unavailable",
                    "description": "股票数据查询工具（开发中）"
                }
            ]
        }
    }

