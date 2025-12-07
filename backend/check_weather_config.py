"""
检查天气 API 配置
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings

print("=" * 60)
print("天气 API 配置检查")
print("=" * 60)

print(f"\n心知天气配置:")
print(f"  WEATHER_API_UID: {settings.WEATHER_API_UID or '未配置'}")
if settings.WEATHER_API_UID:
    uid_preview = settings.WEATHER_API_UID[:10] + "..." + settings.WEATHER_API_UID[-4:] if len(settings.WEATHER_API_UID) > 14 else settings.WEATHER_API_UID
    print(f"   预览: {uid_preview}")

print(f"  WEATHER_API_SECRET: {'已配置' if settings.WEATHER_API_SECRET else '未配置'}")
if settings.WEATHER_API_SECRET:
    secret_preview = settings.WEATHER_API_SECRET[:10] + "..." + settings.WEATHER_API_SECRET[-4:] if len(settings.WEATHER_API_SECRET) > 14 else "***"
    print(f"   预览: {secret_preview}")

print(f"\n和风天气配置:")
print(f"  WEATHER_API_KEY: {settings.WEATHER_API_KEY or '未配置'}")
if settings.WEATHER_API_KEY:
    key_preview = settings.WEATHER_API_KEY[:10] + "..." + settings.WEATHER_API_KEY[-4:] if len(settings.WEATHER_API_KEY) > 14 else settings.WEATHER_API_KEY
    print(f"   预览: {key_preview}")

print(f"\n优先级判断:")
if settings.WEATHER_API_UID and settings.WEATHER_API_SECRET:
    print("  ✓ 将使用心知天气 API（优先级最高）")
elif settings.WEATHER_API_KEY:
    print("  ○ 将使用和风天气 API（降级方案）")
else:
    print("  ✗ 将使用 Mock 数据（未配置任何 API）")

print("\n" + "=" * 60)




