"""
测试天气 API 是否正常工作
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.tools.weather import get_weather

def test_weather_api():
    """测试天气 API"""
    print("=" * 50)
    print("天气 API 测试")
    print("=" * 50)
    
    # 检查 API Key
    api_key = settings.WEATHER_API_KEY
    if api_key:
        print(f"✓ API Key 已配置: {api_key[:10]}...")
    else:
        print("✗ API Key 未配置，将使用 Mock 数据")
        print("  请在 .env 文件中设置: WEATHER_API_KEY=your_api_key")
        return
    
    # 测试查询
    test_cases = [
        {"location": "北京", "days": 3},
        {"location": "上海", "days": 2},
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n测试 {i}: 查询 {params['location']} 未来 {params['days']} 天天气")
        print("-" * 50)
        
        result = get_weather(params)
        
        if result["success"]:
            data = result["data"]
            is_mock = result["metadata"].get("is_mock", True)
            
            if is_mock:
                print("⚠ 使用了 Mock 数据（API 调用可能失败）")
            else:
                print("✓ 使用了真实 API 数据")
            
            print(f"城市: {data['location']}")
            print(f"预报天数: {len(data['forecast'])}")
            
            # 显示前3天的数据
            for day in data['forecast'][:3]:
                print(f"  {day['date']}: {day['weather']}, "
                      f"温度 {day['minTemp']}°C - {day['maxTemp']}°C, "
                      f"湿度 {day['humidity']}%, 风向 {day['wind']}")
        else:
            print(f"✗ 查询失败: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_weather_api()


