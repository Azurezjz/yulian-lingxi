"""
大模型配置和调用测试脚本

使用方法：
1. 确保已配置 .env 文件中的 LLM_API_KEY
2. 运行：python test_llm.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.core.llm_service import LLMService
from app.core.agent import Agent

def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def check_config():
    """检查大模型配置"""
    print_section("1. 检查大模型配置")
    
    has_api_key = bool(settings.LLM_API_KEY)
    has_base_url = bool(settings.LLM_BASE_URL)
    
    print(f"LLM_API_KEY: {'✓ 已配置' if has_api_key else '✗ 未配置'}")
    if has_api_key:
        # 只显示前10个字符和后4个字符
        key_preview = settings.LLM_API_KEY[:10] + "..." + settings.LLM_API_KEY[-4:] if len(settings.LLM_API_KEY) > 14 else "***"
        print(f"  Key 预览: {key_preview}")
    
    print(f"LLM_BASE_URL: {settings.LLM_BASE_URL or '未配置（将使用默认 DashScope 端点）'}")
    print(f"LLM_MODEL: {settings.LLM_MODEL}")
    
    if not has_api_key:
        print("\n⚠️  警告: 未配置 LLM_API_KEY，将使用规则识别（降级方案）")
        print("   如需使用大模型，请在 .env 文件中配置：")
        print("   LLM_API_KEY=你的API_KEY")
        print("   LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1")
        print("   LLM_MODEL=qwen-turbo")
        return False
    
    return True

async def test_llm_service():
    """测试 LLMService 直接调用"""
    print_section("2. 测试 LLMService 直接调用")
    
    llm_service = LLMService()
    
    # 测试消息
    test_messages = [
        {
            "role": "system",
            "content": "你是一个智能助手，负责分析用户需求并选择合适的工具。请严格按照 JSON 格式返回结果。"
        },
        {
            "role": "user",
            "content": "用户需求：查北京天气\n\n返回格式：JSON 格式，包含 tool 和 parameters 字段"
        }
    ]
    
    print("发送测试消息...")
    print(f"  用户输入: 查北京天气")
    
    try:
        result = await llm_service.chat(
            messages=test_messages,
            temperature=0.3,
            user_input="查北京天气"
        )
        
        print(f"\n✓ LLMService 调用成功")
        print(f"  返回结果（前200字符）: {result[:200]}...")
        
        # 尝试解析 JSON
        import json
        try:
            parsed = json.loads(result)
            print(f"  ✓ 返回格式正确（JSON）")
            print(f"  识别工具: {parsed.get('tool', '未知')}")
            print(f"  参数: {parsed.get('parameters', {})}")
        except:
            print(f"  ⚠️  返回格式不是 JSON，可能是大模型返回了其他格式")
        
        return True
        
    except Exception as e:
        print(f"\n✗ LLMService 调用失败: {e}")
        print(f"  错误类型: {type(e).__name__}")
        import traceback
        print(f"  错误详情:\n{traceback.format_exc()}")
        return False

async def test_agent():
    """测试 Agent 意图识别"""
    print_section("3. 测试 Agent 意图识别")
    
    agent = Agent()
    
    # 测试用例
    test_cases = [
        "查北京天气",
        "我想知道上海明天会不会下雨",
        "抓取最近的国内 AI 新闻，列出 3 条并总结",
        "计算 123 乘以 456 等于多少"
    ]
    
    success_count = 0
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {user_input}")
        try:
            result = await agent.execute(user_input)
            
            tool_name = result.get("tool_name", "unknown")
            tool_params = result.get("tool_params", {})
            tool_result = result.get("tool_result", {})
            
            print(f"  ✓ 识别成功")
            print(f"    工具: {tool_name}")
            print(f"    参数: {tool_params}")
            
            if tool_result and tool_result.get("success"):
                print(f"    工具执行: ✓ 成功")
                success_count += 1
            else:
                print(f"    工具执行: ✗ 失败")
                if tool_result:
                    print(f"    错误: {tool_result.get('error', '未知错误')}")
            
        except Exception as e:
            print(f"  ✗ 测试失败: {e}")
    
    print(f"\n测试结果: {success_count}/{len(test_cases)} 个用例成功")
    return success_count > 0

async def test_complex_queries():
    """测试复杂查询（需要大模型理解）"""
    print_section("4. 测试复杂查询（验证大模型能力）")
    
    agent = Agent()
    
    # 这些查询需要大模型理解，规则识别可能无法正确处理
    complex_queries = [
        "我想知道北京明天会不会下雨",
        "帮我找一些关于人工智能的最新消息",
        "如果明天北京下雨，我需要带伞吗？"
    ]
    
    print("这些查询需要大模型理解自然语言：")
    for query in complex_queries:
        print(f"  - {query}")
    
    print("\n开始测试...")
    
    for query in complex_queries:
        print(f"\n查询: {query}")
        try:
            result = await agent.execute(query)
            tool_name = result.get("tool_name", "unknown")
            print(f"  识别结果: {tool_name}")
            
            # 如果识别为 weather 或 news，说明大模型可能在工作
            if tool_name in ["weather", "news"]:
                print(f"  ✓ 可能使用了大模型（规则识别通常无法理解这种复杂表达）")
            else:
                print(f"  ⚠️  可能使用了规则识别")
                
        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

def main():
    """主函数"""
    print_section("大模型配置和调用测试")
    
    # 1. 检查配置
    has_config = check_config()
    
    if not has_config:
        print("\n⚠️  未配置大模型，跳过后续测试")
        print("   系统将使用规则识别（降级方案）")
        return
    
    # 2. 运行异步测试
    async def run_tests():
        # 测试 LLMService
        llm_ok = await test_llm_service()
        
        if llm_ok:
            # 测试 Agent
            await test_agent()
            
            # 测试复杂查询
            await test_complex_queries()
        else:
            print("\n⚠️  LLMService 测试失败，跳过后续测试")
            print("   请检查：")
            print("   1. API Key 是否正确")
            print("   2. base_url 是否正确")
            print("   3. 网络连接是否正常")
            print("   4. API 服务是否可用")
    
    # 运行异步测试
    asyncio.run(run_tests())
    
    print_section("测试完成")
    print("\n提示：")
    print("- 如果看到 '[DEBUG] LLM 降级方案'，说明未使用大模型")
    print("- 如果看到 '[DEBUG] 大模型 API 调用成功'，说明正在使用大模型")
    print("- 如果看到错误信息，请根据错误提示检查配置")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

