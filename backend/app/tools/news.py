"""
新闻检索工具

使用 NewsAPI 获取真实新闻数据
如果没有配置 API Key，则使用 Mock 数据
参考 docs/TOOL_GUIDE.md 中的规范
"""
from typing import Dict, Any
import time
import requests
from app.config import settings

def search_news(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    新闻检索工具
    
    Args:
        params: 参数字典
            - query: 搜索关键词（必填）
            - limit: 返回数量（可选，默认10）
            - category: 分类（可选）
        
    Returns:
        工具执行结果
    """
    start_time = time.time()
    
    # 参数校验
    query = params.get("query")
    if not query:
        return {
            "success": False,
            "data": None,
            "error": "参数错误：query 不能为空",
            "metadata": {
                "tool_name": "news",
                "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    limit = params.get("limit", 10)
    limit = min(limit, 50)  # 最多50条
    category = params.get("category", "")
    
    # 尝试使用真实 API
    api_key = settings.NEWS_API_KEY
    
    if api_key:
        try:
            print(f"[DEBUG] 使用 NewsAPI - 查询: {query}, 数量: {limit}")
            
            # 使用 NewsAPI
            # 注意：免费版需要使用 HTTP（非 HTTPS）进行开发
            # 生产环境可以使用 HTTPS
            news_url = "https://newsapi.org/v2/everything"
            news_params = {
                "q": query,
                "pageSize": limit,
                "sortBy": "publishedAt",
                "apiKey": api_key
            }
            
            # 语言设置：根据查询关键词判断
            if any(ord(char) > 127 for char in query):
                # 包含中文字符，尝试中文搜索
                news_params["language"] = "zh"
            else:
                # 英文关键词，使用英文
                news_params["language"] = "en"
            
            print(f"[DEBUG] NewsAPI 请求参数: q={query}, language={news_params.get('language')}, pageSize={limit}")
            
            response = requests.get(news_url, params=news_params, timeout=10)
            
            # 检查 HTTP 状态码
            if response.status_code == 401:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("message", "API Key 无效或未激活")
                raise ValueError(f"NewsAPI 认证失败 (401): {error_msg}。请检查 API Key 是否正确。")
            
            if response.status_code == 429:
                raise ValueError("NewsAPI 请求频率超限 (429)。免费版每天限制 100 次请求。")
            
            response.raise_for_status()
            data = response.json()
            
            # 检查 API 返回状态
            if data.get("status") == "ok":
                articles_data = data.get("articles", [])
                total_results = data.get("totalResults", 0)
                
                print(f"[DEBUG] NewsAPI 返回成功 - 找到 {total_results} 条结果，返回前 {min(limit, len(articles_data))} 条")
                
                articles = []
                for item in articles_data[:limit]:
                    # 过滤掉没有标题或 URL 的文章
                    if item.get("title") and item.get("url"):
                        # 处理日期格式
                        published_at = item.get("publishedAt", "")
                        # 如果日期格式是 ISO 8601，尝试解析并格式化
                        if published_at:
                            try:
                                from datetime import datetime
                                # 尝试解析 ISO 8601 格式的日期
                                if "T" in published_at:
                                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                                    # 转换为本地时区的日期字符串
                                    published_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    # 如果已经是格式化好的日期，直接使用
                                    pass
                            except Exception as e:
                                print(f"[WARNING] 日期解析失败: {published_at}, 错误: {e}")
                                # 如果解析失败，使用原始值
                                pass
                        
                        articles.append({
                            "title": item.get("title", ""),
                            "source": item.get("source", {}).get("name", "Unknown"),
                            "url": item.get("url", ""),
                            "publishedAt": published_at,
                            "description": item.get("description", "")
                        })
                
                if not articles:
                    raise ValueError("NewsAPI 返回的文章列表为空或格式不正确")
                
                return {
                    "success": True,
                    "data": {
                        "articles": articles,
                        "total": len(articles),
                        "totalResults": total_results
                    },
                    "error": None,
                    "metadata": {
                        "tool_name": "news",
                        "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_mock": False,
                        "api_provider": "newsapi"
                    }
                }
            else:
                error_msg = data.get("message", "Unknown error")
                error_code = data.get("code", "Unknown")
                raise ValueError(f"NewsAPI 返回错误 (code: {error_code}): {error_msg}")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] NewsAPI 网络请求失败：{e}")
            print("[INFO] 降级到 Mock 数据")
        except ValueError as e:
            print(f"[ERROR] NewsAPI 数据错误：{e}")
            print("[INFO] 降级到 Mock 数据")
        except Exception as e:
            import traceback
            print(f"[ERROR] NewsAPI 调用失败：{e}")
            print(f"[ERROR] 错误详情：{traceback.format_exc()}")
            print("[INFO] 降级到 Mock 数据")
    else:
        print(f"[DEBUG] NewsAPI 未配置，使用 Mock 数据")
    
    # 降级到 Mock 数据（当没有 API Key 或 API 调用失败时）
    from datetime import datetime, timedelta
    import random
    
    # 根据查询关键词生成相关新闻
    news_templates = {
        "ai": [
            {"title": "OpenAI 发布最新 GPT 模型", "source": "TechCrunch"},
            {"title": "AI 技术在医疗领域取得突破", "source": "Science Daily"},
            {"title": "欧盟通过 AI 监管法案", "source": "Reuters"},
        ],
        "科技": [
            {"title": "量子计算技术新突破", "source": "科技日报"},
            {"title": "5G 网络覆盖率达到新高度", "source": "通信世界"},
            {"title": "新能源汽车销量创新高", "source": "汽车之家"},
        ],
        "财经": [
            {"title": "股市今日大幅上涨", "source": "财经网"},
            {"title": "央行发布最新货币政策", "source": "第一财经"},
            {"title": "房地产市场政策调整", "source": "新浪财经"},
        ],
    }
    
    # 根据查询关键词选择新闻模板
    selected_news = []
    query_lower = query.lower()
    if "ai" in query_lower or "人工智能" in query_lower or "大模型" in query_lower:
        selected_news = news_templates.get("ai", [])
    elif "科技" in query_lower or "技术" in query_lower:
        selected_news = news_templates.get("科技", [])
    elif "财经" in query_lower or "经济" in query_lower or "股票" in query_lower:
        selected_news = news_templates.get("财经", [])
    else:
        # 默认新闻
        selected_news = news_templates.get("ai", [])
    
    # 生成新闻列表
    articles = []
    for i in range(min(limit, len(selected_news) if selected_news else 3)):
        if selected_news:
            news_item = selected_news[i % len(selected_news)]
        else:
            news_item = {"title": f"关于 {query} 的最新报道", "source": "新闻来源"}
        
        # 生成不同的日期，确保每条新闻的日期都不同
        hours_ago = random.randint(1, 24) + i  # 确保每条新闻的日期不同
        published_date = datetime.now() - timedelta(hours=hours_ago)
        published_at_str = published_date.strftime("%Y-%m-%d %H:%M:%S")
        
        articles.append({
            "title": news_item["title"],
            "source": news_item["source"],
            "url": f"https://example.com/news/{i+1}",
            "publishedAt": published_at_str,  # 使用更易读的日期格式
            "description": f"这是关于 {query} 的新闻摘要，包含相关信息和最新动态。"
        })
    
    return {
        "success": True,
        "data": {
            "articles": articles,
            "total": len(articles)
        },
        "error": None,
        "metadata": {
            "tool_name": "news",
            "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_mock": True
        }
    }
