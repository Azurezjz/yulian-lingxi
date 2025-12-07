"""
天气查询工具

支持心知天气 API 和和风天气 API 获取真实天气数据
如果没有配置 API Key，则使用 Mock 数据
参考 docs/TOOL_GUIDE.md 中的规范
"""
from typing import Dict, Any
import time
import requests
import hmac
import hashlib
import base64
import urllib.parse
from app.config import settings

def generate_seniverse_signature(uid: str, secret: str, ttl: int = 300) -> tuple:
    """
    生成心知天气 API 签名（已弃用，改用直接使用私钥方式）
    
    注意：当前使用直接使用私钥的方式（key=私钥），更简单且已验证可用
    如果需要使用签名验证方式，可以取消注释下面的代码
    
    Args:
        uid: 公钥
        secret: 私钥
        ttl: 签名有效期（秒），默认300秒
        
    Returns:
        (时间戳, 签名) 元组
    """
    # 签名生成代码（已弃用，保留供参考）
    ts = int(time.time())
    params = {
        "ts": ts,
        "ttl": ttl,
        "uid": uid
    }
    
    # 按参数名字典序排列
    sorted_params = sorted(params.items())
    param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    # 使用 HMAC-SHA1 生成签名
    signature = hmac.new(
        secret.encode('utf-8'),
        param_string.encode('utf-8'),
        hashlib.sha1
    ).digest()
    
    # Base64 编码
    sig_base64 = base64.b64encode(signature).decode('utf-8')
    
    # URL 编码（心知天气要求）
    sig = urllib.parse.quote(sig_base64, safe='')
    
    return ts, sig

def get_weather(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    天气查询工具
    
    Args:
        params: 参数字典
            - location: 城市名称（必填）
            - days: 查询天数（可选，默认7）
        
    Returns:
        工具执行结果
    """
    start_time = time.time()
    
    # 参数校验
    location = params.get("location")
    if not location:
        return {
            "success": False,
            "data": None,
            "error": "参数错误：location 不能为空",
            "metadata": {
                "tool_name": "weather",
                "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    days = params.get("days", 7)
    days = min(days, 7)  # 最多7天
    
    # 调试：检查配置
    print(f"[DEBUG] 天气 API 配置检查:")
    print(f"  WEATHER_API_UID: {'已配置' if settings.WEATHER_API_UID else '未配置'}")
    print(f"  WEATHER_API_SECRET: {'已配置' if settings.WEATHER_API_SECRET else '未配置'}")
    print(f"  WEATHER_API_KEY: {'已配置' if settings.WEATHER_API_KEY else '未配置'}")
    
    # 优先使用心知天气 API（如果配置了 UID 和 SECRET）
    if settings.WEATHER_API_UID and settings.WEATHER_API_SECRET:
        try:
            print(f"[DEBUG] 使用心知天气 API - 城市: {location}, 天数: {days}")
            
            # 直接使用私钥方式（更简单，已验证可用）
            api_url = "https://api.seniverse.com/v3/weather/daily.json"
            api_params = {
                "key": settings.WEATHER_API_SECRET,  # 直接使用私钥
                "location": location,
                "language": "zh-Hans",
                "unit": "c",
                "start": 0,
                "days": days
            }
            
            print(f"[DEBUG] 心知天气 API 调用 - 使用私钥方式")
            response = requests.get(api_url, params=api_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 检查 API 返回状态
            if "results" not in data or not data["results"]:
                raise ValueError("心知天气 API 返回数据格式错误")
            
            result = data["results"][0]
            location_name = result.get("location", {}).get("name", location)
            daily_data = result.get("daily", [])
            
            if not daily_data:
                raise ValueError("心知天气 API 返回数据为空")
            
            # 辅助函数：解析温度值（处理字符串或数字格式）
            def parse_temp(temp_value):
                """解析温度值，支持字符串格式（如 '15°C'）或数字格式"""
                if isinstance(temp_value, (int, float)):
                    return int(temp_value)
                if isinstance(temp_value, str):
                    # 移除温度单位符号
                    temp_str = temp_value.replace("°C", "").replace("℃", "").replace("°", "").strip()
                    try:
                        return int(float(temp_str))
                    except:
                        return 0
                return 0
            
            # 转换数据格式
            forecast = []
            for i, day_data in enumerate(daily_data[:days]):
                date = day_data.get("date", "")
                
                # 温度（摄氏度）
                temp_max = parse_temp(day_data.get("high", 0))
                temp_min = parse_temp(day_data.get("low", 0))
                
                # 天气描述
                text_day = day_data.get("text_day", "未知")
                text_night = day_data.get("text_night", "未知")
                weather = f"{text_day}" if text_day == text_night else f"{text_day}转{text_night}"
                
                # 湿度（心知天气可能不提供，使用默认值）
                humidity = int(day_data.get("humidity", 50))
                
                # 风向和风力
                wind_dir = day_data.get("wind_direction", "无风")
                wind_scale = day_data.get("wind_scale", "0")
                wind = f"{wind_dir} {wind_scale}级"
                
                forecast.append({
                    "date": date,
                    "weather": weather,
                    "maxTemp": temp_max,
                    "minTemp": temp_min,
                    "humidity": humidity,
                    "wind": wind
                })
            
            print(f"[DEBUG] 心知天气 API 调用成功 - 城市: {location_name}, 返回 {len(forecast)} 天数据")
            
            return {
                "success": True,
                "data": {
                    "location": location_name,
                    "forecast": forecast
                },
                "error": None,
                "metadata": {
                    "tool_name": "weather",
                    "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_mock": False,
                    "api_provider": "seniverse"
                }
            }
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 心知天气 API 网络请求失败：{e}")
            print("[INFO] 降级到和风天气或 Mock 数据")
        except ValueError as e:
            print(f"[ERROR] 心知天气 API 数据错误：{e}")
            print("[INFO] 降级到和风天气或 Mock 数据")
        except Exception as e:
            import traceback
            print(f"[ERROR] 心知天气 API 调用失败：{e}")
            print(f"[ERROR] 错误详情：{traceback.format_exc()}")
            print("[INFO] 降级到和风天气或 Mock 数据")
    else:
        print(f"[DEBUG] 心知天气 API 未配置（UID 或 SECRET 为空），跳过心知天气")
    
    # 降级到和风天气 API（如果配置了 WEATHER_API_KEY）
    api_key = settings.WEATHER_API_KEY
    
    if api_key:
        print(f"[DEBUG] 使用和风天气 API - 城市: {location}, 天数: {days}")
        try:
            # 使用和风天气 API
            # 和风天气可以直接使用城市名称查询，也可以先获取城市 ID
            # 先尝试直接使用城市名称查询（更简单，避免城市搜索 API 的问题）
            location_param = location
            city_name = location  # 默认使用输入的城市名
            
            # 尝试先获取城市 ID（可选，如果失败则直接使用城市名称）
            try:
                city_search_url = "https://geoapi.qweather.com/v2/city/lookup"
                city_params = {
                    "location": location
                }
                
                # 优先使用请求标头方式（推荐）
                city_headers = {
                    "X-QW-Api-Key": api_key
                }
                
                city_response = requests.get(
                    city_search_url, 
                    params=city_params, 
                    headers=city_headers,
                    timeout=5
                )
                
                # 如果请求标头方式失败（401/403），尝试请求参数方式（降级方案）
                if city_response.status_code in [401, 403, 404]:
                    print(f"[DEBUG] 和风天气 - 请求标头方式失败 (HTTP {city_response.status_code})，尝试请求参数方式")
                    city_params_with_key = {
                        "location": location,
                        "key": api_key
                    }
                    city_response = requests.get(
                        city_search_url,
                        params=city_params_with_key,
                        timeout=5
                    )
                
                if city_response.status_code == 200:
                    city_data = city_response.json()
                    if city_data.get("code") == "200" and city_data.get("location"):
                        location_list = city_data.get("location", [])
                        if location_list:
                            location_param = location_list[0]["id"]
                            city_name = location_list[0].get("name", location)
                            print(f"[DEBUG] 和风天气 - 获取城市 ID 成功: {city_name} (ID: {location_param})")
                else:
                    print(f"[DEBUG] 和风天气 - 城市搜索失败 (HTTP {city_response.status_code})，将直接使用城市名称")
            except Exception as e:
                print(f"[DEBUG] 和风天气 - 城市搜索异常: {e}，将直接使用城市名称")
            
            # 获取天气预报（和风天气支持7天预报）
            forecast_url = "https://devapi.qweather.com/v7/weather/7d"
            days = min(days, 7)  # 和风天气免费版最多7天
            
            forecast_params = {
                "location": location_param  # 使用城市 ID 或城市名称
            }
            
            # 优先使用请求标头方式（推荐）
            forecast_headers = {
                "X-QW-Api-Key": api_key
            }
            
            forecast_response = requests.get(
                forecast_url, 
                params=forecast_params, 
                headers=forecast_headers,
                timeout=10
            )
            
            # 如果请求标头方式失败（401/403），尝试请求参数方式（降级方案）
            if forecast_response.status_code in [401, 403, 404]:
                print(f"[DEBUG] 和风天气 - 请求标头方式失败 (HTTP {forecast_response.status_code})，尝试请求参数方式")
                forecast_params_with_key = {
                    "location": location_param,
                    "key": api_key
                }
                forecast_response = requests.get(
                    forecast_url,
                    params=forecast_params_with_key,
                    timeout=10
                )
            
            # 检查天气预报的 HTTP 状态码
            if forecast_response.status_code == 401:
                error_data = forecast_response.json() if forecast_response.text else {}
                error_msg = error_data.get("message", "API Key 无效或未激活")
                raise ValueError(f"和风天气 API 认证失败 (401): {error_msg}。请检查 API Key 是否正确。")
            
            if forecast_response.status_code == 403:
                error_data = forecast_response.json() if forecast_response.text else {}
                error_msg = error_data.get("message", "访问被拒绝")
                raise ValueError(f"和风天气 API 访问被拒绝 (403): {error_msg}。可能是 API Key 权限不足或未激活天气预报服务。")
            
            if forecast_response.status_code == 404:
                raise ValueError(f"和风天气 API 端点不存在 (404)。请检查 API 端点是否正确，或访问 https://dev.qweather.com/docs/api/ 查看最新文档。")
            
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # 检查 API 返回状态
            if forecast_data.get("code") != "200":
                error_msg = forecast_data.get("message", "未知错误")
                error_code = forecast_data.get("code", "未知")
                raise ValueError(f"天气查询失败 (code: {error_code}): {error_msg}")
            
            # 解析数据
            from datetime import datetime
            daily_forecast = forecast_data.get("daily", [])
            
            if not daily_forecast:
                raise ValueError("API 返回数据为空")
            
            # 使用从城市搜索获取的城市名称
            
            # 转换数据格式
            forecast = []
            for i, day_data in enumerate(daily_forecast[:days]):
                # 和风天气的日期格式是 YYYY-MM-DD
                date = day_data.get("fxDate", "")
                
                # 温度（摄氏度）
                temp_max = int(day_data.get("tempMax", 0))
                temp_min = int(day_data.get("tempMin", 0))
                
                # 天气描述
                text_day = day_data.get("textDay", "未知")
                text_night = day_data.get("textNight", "未知")
                weather = f"{text_day}" if text_day == text_night else f"{text_day}转{text_night}"
                
                # 湿度
                humidity = int(day_data.get("humidity", 0))
                
                # 风向和风力
                wind_dir_day = day_data.get("windDirDay", "无风")
                wind_scale_day = day_data.get("windScaleDay", "0")
                wind = f"{wind_dir_day} {wind_scale_day}级"
                
                forecast.append({
                    "date": date,
                    "weather": weather,
                    "maxTemp": temp_max,
                    "minTemp": temp_min,
                    "humidity": humidity,
                    "wind": wind
                })
            
            return {
                "success": True,
                "data": {
                    "location": city_name,
                    "forecast": forecast
                },
                "error": None,
                "metadata": {
                    "tool_name": "weather",
                    "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_mock": False
                }
            }
        except requests.exceptions.RequestException as e:
            # 网络请求失败
            print(f"天气 API 网络请求失败：{e}")
            print("降级到 Mock 数据")
        except ValueError as e:
            # 数据解析错误
            print(f"天气 API 数据错误：{e}")
            print("降级到 Mock 数据")
        except Exception as e:
            # 其他错误
            import traceback
            print(f"天气 API 调用失败：{e}")
            print(f"错误详情：{traceback.format_exc()}")
            print("降级到 Mock 数据")
    
    # 降级到 Mock 数据（当没有 API Key 或 API 调用失败时）
    from datetime import datetime, timedelta
    import hashlib
    
    # 根据城市生成不同的基础温度（模拟不同城市的气候，更符合实际）
    # 冬季温度参考（1月份）
    city_base_temp = {
        "北京": 2, "上海": 8, "广州": 18, "深圳": 19, "杭州": 6,
        "南京": 4, "成都": 7, "武汉": 5, "西安": 2, "天津": 1,
        "重庆": 9, "苏州": 6, "长沙": 7, "郑州": 3, "青岛": 2, "大连": -1,
        "济南": 2, "福州": 13, "厦门": 15, "合肥": 4, "石家庄": 1,
        "哈尔滨": -18, "长春": -15, "沈阳": -10
    }
    base_temp = city_base_temp.get(location, 5)
    
    # 使用确定性算法生成数据（基于城市和日期，确保相同输入返回相同结果）
    forecast = []
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        
        # 使用城市名称和日期生成确定性哈希值
        hash_input = f"{location}_{date}_{i}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 基于哈希值生成确定性但看起来随机的数据
        # 温度变化范围：基础温度 ± 5度
        temp_variation = (hash_value % 11) - 5  # -5 到 +5
        max_temp = base_temp + temp_variation
        min_temp = max_temp - (hash_value % 8 + 3)  # 最低温度比最高温度低3-10度
        
        # 湿度：40-80%
        humidity = 40 + (hash_value % 41)
        
        # 天气类型
        weather_types = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Foggy"]
        weather = weather_types[hash_value % len(weather_types)]
        
        # 风向和风力
        wind_directions = ["North", "South", "East", "West", "Northeast", "Southwest", "Northwest", "Southeast"]
        wind_dir = wind_directions[hash_value % len(wind_directions)]
        wind_speed = 2 + (hash_value % 4)  # 2-5级
        wind = f"{wind_dir} {wind_speed}"
        
        forecast.append({
            "date": date,
            "weather": weather,
            "maxTemp": max_temp,
            "minTemp": min_temp,
            "humidity": humidity,
            "wind": wind
        })
    
    return {
        "success": True,
        "data": {
            "location": location,
            "forecast": forecast
        },
        "error": None,
        "metadata": {
            "tool_name": "weather",
            "duration": f"{(time.time() - start_time) * 1000:.0f}ms",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_mock": True
        }
    }
