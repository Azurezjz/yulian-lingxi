"""
文档生成工具

使用大模型生成各类文档（报告、邮件、总结等）
如果没有配置大模型，则使用 Mock 数据
参考 docs/TOOL_GUIDE.md 中的规范
"""
from typing import Dict, Any
import time
import asyncio
import json
from app.core.llm_service import LLMService
from app.config import settings

def _build_document_prompt(template: str, content: str, data: Dict[str, Any] = None) -> str:
    """
    构建文档生成提示词
    
    Args:
        template: 模板类型（report、email、summary）
        content: 内容提示
        data: 上下文数据（可选）
        
    Returns:
        提示词字符串
    """
    # 模板说明
    template_descriptions = {
        "report": "报告",
        "email": "邮件",
        "summary": "总结"
    }
    
    template_name = template_descriptions.get(template.lower(), "文档")
    
    # 构建基础提示词
    prompt = f"请生成一份{template_name}，要求如下：\n\n"
    prompt += f"主题/内容：{content}\n\n"
    
    # 如果有上下文数据，添加到提示词中
    if data:
        prompt += "上下文数据：\n"
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    prompt += f"- {key}: {json.dumps(value, ensure_ascii=False, indent=2)}\n"
                else:
                    prompt += f"- {key}: {value}\n"
        prompt += "\n"
    
    # 根据模板类型添加特定要求
    if template.lower() == "report":
        prompt += """请按照以下格式生成报告：
1. 标题
2. 概述/摘要
3. 主要内容（分点说明）
4. 结论/建议

使用 Markdown 格式，确保内容专业、清晰、有条理。"""
    elif template.lower() == "email":
        prompt += """请按照以下格式生成邮件：
1. 主题行
2. 称呼
3. 正文（简洁明了）
4. 结尾

使用 Markdown 格式，语气要专业但友好。"""
    elif template.lower() == "summary":
        prompt += """请生成一份简洁的总结：
1. 核心要点
2. 关键信息
3. 简要结论

使用 Markdown 格式，内容要精炼、重点突出。"""
    else:
        prompt += "请使用 Markdown 格式生成文档，内容要专业、清晰。"
    
    return prompt

async def _generate_with_llm(template: str, content: str, data: Dict[str, Any] = None) -> str:
    """
    使用大模型生成文档内容（异步函数）
    
    Args:
        template: 模板类型
        content: 内容提示
        data: 上下文数据
        
    Returns:
        生成的文档内容
    """
    llm_service = LLMService()
    
    # 构建提示词
    prompt = _build_document_prompt(template, content, data)
    
    # 构建消息
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的文档生成助手，擅长生成各种类型的文档。请根据用户要求生成高质量的文档内容，使用 Markdown 格式。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    # 调用大模型（使用较高的 temperature 以获得更自然的文本）
    response = await llm_service.chat(messages, temperature=0.8, user_input=content)
    
    return response

def generate_document(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    文档生成工具
    
    Args:
        params: 参数字典
            - template: 文档模板类型（必填，report/email/summary）
            - content: 内容提示（必填）
            - data: 上下文数据（可选）
            - format: 输出格式（可选，默认 "markdown"）
        
    Returns:
        工具执行结果
    """
    start_time = time.time()
    
    # 参数校验
    template = params.get("template")
    content = params.get("content")
    if not template or not content:
        return {
            "success": False,
            "data": None,
            "error": "参数错误：template 和 content 不能为空",
            "metadata": {
                "tool_name": "document",
                "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    data = params.get("data", {})
    format_type = params.get("format", "markdown")
    
    # 尝试使用大模型生成文档
    if settings.LLM_API_KEY:
        try:
            print(f"[DEBUG] 使用大模型生成文档 - 模板: {template}, 内容提示: {content[:50]}...")
            
            # 调用异步函数生成文档
            # 由于 generate_document 是在 asyncio.to_thread 中运行的同步函数，
            # 它不在异步上下文中，可以直接使用 asyncio.run()
            # 如果 asyncio.run() 失败（已有事件循环），则创建新的事件循环
            try:
                document_content = asyncio.run(_generate_with_llm(template, content, data))
            except RuntimeError:
                # 如果已经有事件循环在运行，创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    document_content = loop.run_until_complete(_generate_with_llm(template, content, data))
                finally:
                    loop.close()
            
            # 计算字数
            word_count = len(document_content)
            
            print(f"[DEBUG] 文档生成成功 - 字数: {word_count}")
            
            return {
                "success": True,
                "data": {
                    "content": document_content,
                    "format": format_type,
                    "word_count": word_count,
                    "template": template
                },
                "error": None,
                "metadata": {
                    "tool_name": "document",
                    "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_mock": False,
                    "api_provider": "llm"
                }
            }
        except asyncio.TimeoutError:
            print(f"[ERROR] 文档生成超时（超过30秒）")
            print("[INFO] 降级到 Mock 数据")
        except Exception as e:
            import traceback
            print(f"[ERROR] 文档生成失败：{e}")
            print(f"[ERROR] 错误详情：{traceback.format_exc()}")
            print("[INFO] 降级到 Mock 数据")
    else:
        print(f"[DEBUG] 大模型未配置，使用 Mock 数据")
    
    # 降级到 Mock 数据（当没有大模型或生成失败时）
    # 生成简单的 Mock 文档
    template_names = {
        "report": "报告",
        "email": "邮件",
        "summary": "总结"
    }
    template_name = template_names.get(template.lower(), "文档")
    
    mock_content = f"""# {template_name}

## 主题
{content}

## 内容

这是基于"{content}"生成的{template_name}示例。

### 主要要点

1. 要点一：相关内容
2. 要点二：相关信息
3. 要点三：相关建议

### 总结

以上是关于"{content}"的{template_name}内容。

---
*注：这是 Mock 数据，实际功能需要配置大模型 API Key*
"""
    
    word_count = len(mock_content)
    
    return {
        "success": True,
        "data": {
            "content": mock_content,
            "format": format_type,
            "word_count": word_count,
            "template": template
        },
        "error": None,
        "metadata": {
            "tool_name": "document",
            "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_mock": True
        }
    }


