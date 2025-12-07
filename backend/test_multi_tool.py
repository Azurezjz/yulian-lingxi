"""
测试多工具链式调用功能
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.agent import Agent

async def test_multi_tool():
    """测试多工具链式调用"""
    print("=" * 60)
    print("测试多工具链式调用功能")
    print("=" * 60)
    
    agent = Agent()
    
    # 测试用例 1: 查天气并写总结
    print(f"\n[测试 1] 查天气并写总结")
    print("-" * 60)
    user_input1 = "查北京天气并写总结"
    print(f"用户输入: {user_input1}")
    
    result1 = await agent.execute(user_input1)
    print(f"是否多工具: {result1.get('is_multi_tool', False)}")
    print(f"工具链: {result1.get('tool_chain', [])}")
    
    if result1.get('is_multi_tool'):
        tool_results = result1.get('tool_result', [])
        print(f"工具数量: {len(tool_results)}")
        for i, tool_exec in enumerate(tool_results, 1):
            print(f"\n工具 {i}: {tool_exec.get('tool_name')}")
            tool_res = tool_exec.get('tool_result', {})
            print(f"  成功: {tool_res.get('success', False)}")
            if tool_res.get('success'):
                data = tool_res.get('data', {})
                if 'forecast' in data:
                    print(f"  天气数据: {len(data.get('forecast', []))} 天")
                elif 'content' in data:
                    content = data.get('content', '')
                    print(f"  文档内容: {content[:100]}...")
    else:
        print("未识别为多工具调用")
    
    # 测试用例 2: 查新闻并写总结
    print(f"\n[测试 2] 查新闻并写总结")
    print("-" * 60)
    user_input2 = "抓取最近的AI新闻，列出3条并写总结"
    print(f"用户输入: {user_input2}")
    
    result2 = await agent.execute(user_input2)
    print(f"是否多工具: {result2.get('is_multi_tool', False)}")
    print(f"工具链: {result2.get('tool_chain', [])}")
    
    if result2.get('is_multi_tool'):
        tool_results = result2.get('tool_result', [])
        print(f"工具数量: {len(tool_results)}")
        for i, tool_exec in enumerate(tool_results, 1):
            print(f"\n工具 {i}: {tool_exec.get('tool_name')}")
            tool_res = tool_exec.get('tool_result', {})
            print(f"  成功: {tool_res.get('success', False)}")
            if tool_res.get('success'):
                data = tool_res.get('data', {})
                if 'articles' in data:
                    print(f"  新闻数量: {len(data.get('articles', []))}")
                elif 'content' in data:
                    content = data.get('content', '')
                    print(f"  文档内容: {content[:100]}...")
    else:
        print("未识别为多工具调用")
    
    # 测试用例 3: 单工具调用（应该不是多工具）
    print(f"\n[测试 3] 单工具调用")
    print("-" * 60)
    user_input3 = "查北京天气"
    print(f"用户输入: {user_input3}")
    
    result3 = await agent.execute(user_input3)
    print(f"是否多工具: {result3.get('is_multi_tool', False)}")
    print(f"工具名称: {result3.get('tool_name')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_multi_tool())

