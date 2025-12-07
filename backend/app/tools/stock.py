"""
股票数据查询工具

使用 Alpha Vantage API 获取真实股票数据
如果没有配置 API Key，则使用 Mock 数据
参考 docs/TOOL_GUIDE.md 中的规范
"""
from typing import Dict, Any
import time
import requests
from app.config import settings

def get_stock_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    股票数据查询工具
    
    Args:
        params: 参数字典
            - symbol: 股票代码（必填）
            - days: 查询天数（可选，默认5）
        
    Returns:
        工具执行结果
    """
    start_time = time.time()
    
    # 参数校验
    symbol = params.get("symbol")
    if not symbol:
        return {
            "success": False,
            "data": None,
            "error": "参数错误：symbol 不能为空",
            "metadata": {
                "tool_name": "stock",
                "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    days = params.get("days", 5)
    days = min(max(days, 1), 30)  # 限制在1-30天
    
    # 股票名称到代码的映射（用于将股票名称转换为代码）
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
        print(f"[DEBUG] 股票名称转换: {original_symbol} -> {symbol}")
    
    # 股票代码到名称的映射（用于显示）
    stock_names = {
        "600519": "贵州茅台",
        "000001": "平安银行",
        "00700": "腾讯控股",
        "09988": "阿里巴巴",
        "000002": "万科A",
        "600036": "招商银行",
        "000858": "五粮液"
    }
    stock_name = stock_names.get(symbol, f"股票{symbol}")
    
    # 尝试使用真实 API
    api_key = settings.STOCK_API_KEY
    
    if api_key:
        try:
            # 判断是中国股票还是美国股票
            # 中国股票代码通常是6位数字（上海/深圳）或5位数字（港股）
            # 美国股票代码通常是1-5个字母
            
            # Alpha Vantage 主要支持美国股票（字母代码，如 AAPL, MSFT）
            # 中国股票代码（数字）可能无法直接使用，会降级到 Mock 数据
            # 判断是美股（字母）还是中国股票（数字）
            if symbol.isalpha() and 1 <= len(symbol) <= 5:
                # 美国股票代码（字母，如 AAPL, MSFT, TSLA）
                stock_url = "https://www.alphavantage.co/query"
                stock_params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": symbol.upper(),  # 转换为大写
                    "apikey": api_key,
                    "outputsize": "compact"
                }
                
                print(f"[DEBUG] 使用 Alpha Vantage API - 美股代码: {symbol.upper()}")
                response = requests.get(stock_url, params=stock_params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if "Time Series (Daily)" in data:
                    time_series = data["Time Series (Daily)"]
                    prices = []
                    
                    # 获取最近几天的数据
                    sorted_dates = sorted(time_series.keys(), reverse=True)[:days]
                    
                    for date in sorted_dates:
                        daily_data = time_series[date]
                        prices.append({
                            "date": date,
                            "open": float(daily_data["1. open"]),
                            "close": float(daily_data["4. close"]),
                            "high": float(daily_data["2. high"]),
                            "low": float(daily_data["3. low"]),
                            "volume": int(daily_data["5. volume"])
                        })
                    
                    # 按日期正序排列
                    prices.reverse()
                    
                    return {
                        "success": True,
                        "data": {
                            "symbol": symbol.upper(),
                            "name": stock_name,
                            "prices": prices
                        },
                        "error": None,
                        "metadata": {
                            "tool_name": "stock",
                            "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "is_mock": False,
                            "api_provider": "alphavantage"
                        }
                    }
                elif "Error Message" in data or "Note" in data:
                    # API 限制或错误，降级到 Mock
                    error_msg = data.get('Error Message', data.get('Note', 'Unknown error'))
                    print(f"[WARNING] Alpha Vantage API 错误: {error_msg}")
                    raise ValueError(f"API 错误: {error_msg}")
                else:
                    raise ValueError("API 返回格式错误")
            elif symbol.isdigit() and len(symbol) >= 5:
                # 中国股票代码（数字），Alpha Vantage 不支持，直接使用 Mock 数据
                print(f"[INFO] 中国股票代码 {symbol}，Alpha Vantage 不支持，使用 Mock 数据")
                raise ValueError(f"Alpha Vantage 不支持中国股票代码，使用 Mock 数据")
            else:
                # 非标准格式，降级到 Mock
                print(f"[WARNING] 不支持的股票代码格式: {symbol}，使用 Mock 数据")
                raise ValueError(f"不支持的股票代码格式: {symbol}")
        except Exception as e:
            # API 调用失败，降级到 Mock 数据
            print(f"股票 API 调用失败：{e}，使用 Mock 数据")
    
    # 降级到 Mock 数据（当没有 API Key 或 API 调用失败时）
    from datetime import datetime, timedelta
    import hashlib
    
    # 使用确定性算法生成股票数据
    prices = []
    base_price = 100.0  # 基础价格
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
        
        # 使用股票代码和日期生成确定性哈希值
        hash_input = f"{symbol}_{date}_{i}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 生成价格数据（基于哈希值，确保相同输入返回相同结果）
        price_variation = (hash_value % 21) - 10  # -10 到 +10
        close_price = base_price + price_variation + (i * 0.5)  # 轻微上涨趋势
        open_price = close_price - (hash_value % 3) - 0.5
        high_price = close_price + (hash_value % 2) + 1.0
        low_price = close_price - (hash_value % 3) - 1.0
        volume = 1000000 + (hash_value % 500000)
        
        prices.append({
            "date": date,
            "open": round(open_price, 2),
            "close": round(close_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "volume": volume
        })
    
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "name": stock_name,
            "prices": prices
        },
        "error": None,
        "metadata": {
            "tool_name": "stock",
            "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_mock": True
        }
    }
