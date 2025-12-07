"""
测试 NewsAPI 是否正常工作

使用方法：
python test_news_api.py
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.tools.news import search_news

def test_news_api():
    """测试 NewsAPI"""
    print("=" * 60)
    print("NewsAPI 测试工具")
    print("=" * 60)
    
    # 检查配置
    print("\n配置检查:")
    print(f"  NEWS_API_KEY: {'✓ 已配置' if settings.NEWS_API_KEY else '✗ 未配置'}")
    if settings.NEWS_API_KEY:
        key_preview = settings.NEWS_API_KEY[:10] + "..." + settings.NEWS_API_KEY[-4:] if len(settings.NEWS_API_KEY) > 14 else settings.NEWS_API_KEY
        print(f"   预览: {key_preview}")
    
    if not settings.NEWS_API_KEY:
        print("\n❌ 请先配置 API 密钥")
        print("   在 .env 文件中添加:")
        print("   NEWS_API_KEY=你的API_KEY")
        return
    
    # 测试用例
    test_cases = [
        {"query": "AI", "limit": 3},
        {"query": "科技", "limit": 3},
        {"query": "人工智能", "limit": 3},
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: 查询 '{params['query']}'，返回 {params['limit']} 条")
        print(f"{'='*60}")
        
        result = search_news(params)
        
        if result["success"]:
            data = result["data"]
            is_mock = result["metadata"].get("is_mock", True)
            
            if is_mock:
                print("⚠ 使用了 Mock 数据（API 调用可能失败）")
            else:
                print("✓ 使用了真实 NewsAPI 数据")
            
            print(f"\n返回结果:")
            print(f"  总文章数: {data.get('total', 0)}")
            if "totalResults" in data:
                print(f"  API 总结果数: {data.get('totalResults', 0)}")
            
            articles = data.get("articles", [])
            print(f"\n文章列表:")
            for j, article in enumerate(articles, 1):
                print(f"  {j}. {article.get('title', 'N/A')}")
                print(f"     来源: {article.get('source', 'N/A')}")
                print(f"     时间: {article.get('publishedAt', 'N/A')}")
                if article.get('url'):
                    print(f"     链接: {article.get('url')[:80]}...")
        else:
            print(f"✗ 查询失败: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_news_api()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

