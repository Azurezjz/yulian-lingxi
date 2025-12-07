"""
测试文档生成功能
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.document import generate_document
from app.config import settings

def test_document_generation():
    """测试文档生成功能"""
    print("=" * 60)
    print("测试文档生成功能")
    print("=" * 60)
    
    # 检查配置
    print(f"\n[配置检查]")
    print(f"  LLM_API_KEY: {'已配置' if settings.LLM_API_KEY else '未配置'}")
    print(f"  LLM_BASE_URL: {settings.LLM_BASE_URL or '未配置（使用默认）'}")
    print(f"  LLM_MODEL: {settings.LLM_MODEL}")
    
    # 测试用例 1: 生成报告
    print(f"\n[测试 1] 生成报告")
    print("-" * 60)
    params1 = {
        "template": "report",
        "content": "2024年第一季度销售业绩分析",
        "data": {
            "revenue": 1000000,
            "growth": "15%",
            "region": "华东地区"
        },
        "format": "markdown"
    }
    result1 = generate_document(params1)
    print(f"成功: {result1['success']}")
    print(f"是否 Mock: {result1['metadata'].get('is_mock', False)}")
    print(f"字数: {result1['data']['word_count']}")
    print(f"耗时: {result1['metadata']['duration']}")
    if result1['success']:
        print(f"\n生成的内容（前500字符）:")
        print(result1['data']['content'][:500])
        if len(result1['data']['content']) > 500:
            print("...")
    
    # 测试用例 2: 生成邮件
    print(f"\n[测试 2] 生成邮件")
    print("-" * 60)
    params2 = {
        "template": "email",
        "content": "邀请参加下周的团队会议",
        "data": {
            "date": "2024-03-15",
            "time": "14:00",
            "location": "会议室A"
        },
        "format": "markdown"
    }
    result2 = generate_document(params2)
    print(f"成功: {result2['success']}")
    print(f"是否 Mock: {result2['metadata'].get('is_mock', False)}")
    print(f"字数: {result2['data']['word_count']}")
    print(f"耗时: {result2['metadata']['duration']}")
    if result2['success']:
        print(f"\n生成的内容（前500字符）:")
        print(result2['data']['content'][:500])
        if len(result2['data']['content']) > 500:
            print("...")
    
    # 测试用例 3: 生成总结
    print(f"\n[测试 3] 生成总结")
    print("-" * 60)
    params3 = {
        "template": "summary",
        "content": "AI技术发展趋势",
        "format": "markdown"
    }
    result3 = generate_document(params3)
    print(f"成功: {result3['success']}")
    print(f"是否 Mock: {result3['metadata'].get('is_mock', False)}")
    print(f"字数: {result3['data']['word_count']}")
    print(f"耗时: {result3['metadata']['duration']}")
    if result3['success']:
        print(f"\n生成的内容（前500字符）:")
        print(result3['data']['content'][:500])
        if len(result3['data']['content']) > 500:
            print("...")
    
    # 测试用例 4: 参数错误
    print(f"\n[测试 4] 参数错误测试")
    print("-" * 60)
    params4 = {
        "template": "report"
        # 缺少 content 参数
    }
    result4 = generate_document(params4)
    print(f"成功: {result4['success']}")
    print(f"错误信息: {result4.get('error', '无')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_document_generation()

