"""
提示词模板
"""
from typing import Dict, Any

class PromptTemplate:
    """提示词模板管理"""
    
    INTENT_RECOGNITION_PROMPT = """你是一个智能助手，负责分析用户需求并选择合适的工具。

可用工具列表：
1. weather - 天气查询工具
   - 功能：查询指定城市的天气信息（支持7天预报）
   - 参数：location（城市名称，必填）、days（查询天数，可选，默认7）

2. news - 新闻检索工具
   - 功能：根据关键词检索新闻
   - 参数：query（搜索关键词，必填）、limit（返回数量，可选，默认10）

3. stock - 股票数据查询工具
   - 功能：查询股票历史价格数据
   - 参数：symbol（股票代码，必填）、days（查询天数，可选，默认5）

4. calculate - 数值计算工具
   - 功能：执行数学计算
   - 参数：expression（计算表达式，必填）、variables（变量字典，可选）

5. document - 文档生成工具
   - 功能：生成报告、邮件、总结等文档
   - 参数：template（模板类型，必填，可选值：report/email/summary）、content（内容提示，必填）、data（上下文数据，可选）

请分析以下用户需求，并返回 JSON 格式的工具调用指令。

用户需求：{user_input}

重要说明：
1. 如果用户需求包含多个任务（如"查天气并写总结"、"查天气→绘图→写总结"），请识别所有需要的工具，按顺序返回
2. 如果用户需求包含计算表达式（如"1+1"、"计算"等），优先使用 calculate 工具
3. 如果用户需求包含"总结"、"写总结"、"生成报告"等，通常需要先获取数据（天气/新闻/股票），然后使用 document 工具生成总结
4. 你必须只返回 JSON 格式，不要包含任何其他文本、解释或 markdown 代码块标记

返回格式示例（单个工具）：
{{
    "tool": "weather",
    "parameters": {{
        "location": "北京",
        "days": 7
    }},
    "reasoning": "用户查询天气信息"
}}

返回格式示例（多个工具，按顺序）：
{{
    "tools": [
        {{
            "tool": "weather",
            "parameters": {{
                "location": "北京",
                "days": 7
            }}
        }},
        {{
            "tool": "document",
            "parameters": {{
                "template": "summary",
                "content": "根据天气数据生成总结"
            }}
        }}
    ],
    "reasoning": "用户需要查询天气并生成总结"
}}

如果用户需求包含计算，返回：
{{
    "tool": "calculate",
    "parameters": {{
        "expression": "1+1"
    }},
    "reasoning": "用户需要进行计算"
}}

如果用户需求不需要调用工具，返回：
{{
    "tool": null,
    "reasoning": "用户需求不需要调用工具"
}}
"""
    
    def get_intent_recognition_prompt(self, user_input: str) -> str:
        """获取意图识别提示词"""
        return self.INTENT_RECOGNITION_PROMPT.format(user_input=user_input)
    
    def get_tool_selection_prompt(
        self, 
        user_input: str, 
        previous_results: list = None
    ) -> str:
        """获取工具选择提示词（支持多工具联动）"""
        prompt = """你是一个智能助手，需要根据之前的工具执行结果，选择下一个要调用的工具。

之前的工具执行结果：
"""
        if previous_results:
            for i, result in enumerate(previous_results, 1):
                prompt += f"\n工具 {i}: {result.get('tool_name', 'unknown')}\n"
                prompt += f"结果: {str(result.get('tool_result', {}))[:200]}...\n"
        else:
            prompt += "无\n"
        
        prompt += f"\n用户需求：{user_input}\n"
        prompt += "\n请分析是否需要调用下一个工具，如果需要，返回 JSON 格式的工具调用指令。"
        
        return prompt


