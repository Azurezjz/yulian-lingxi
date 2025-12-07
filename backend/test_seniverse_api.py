"""
测试心知天气 API 签名生成和调用

使用方法：
python test_seniverse_api.py
"""
import sys
from pathlib import Path
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings

def generate_seniverse_signature(uid: str, secret: str, ttl: int = 300) -> tuple:
    """
    生成心知天气 API 签名（带详细日志）
    """
    ts = int(time.time())
    params = {
        "ts": ts,
        "ttl": ttl,
        "uid": uid
    }
    
    print("\n" + "="*60)
    print("步骤 1: 签名生成过程")
    print("="*60)
    print(f"时间戳 (ts): {ts}")
    print(f"有效期 (ttl): {ttl} 秒")
    print(f"公钥 (uid): {uid}")
    
    # 按参数名字典序排列
    sorted_params = sorted(params.items())
    print(f"\n排序后的参数: {sorted_params}")
    
    param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    print(f"参数字符串: {param_string}")
    
    # 使用 HMAC-SHA1 生成签名
    signature = hmac.new(
        secret.encode('utf-8'),
        param_string.encode('utf-8'),
        hashlib.sha1
    ).digest()
    
    print(f"HMAC-SHA1 原始签名 (hex): {signature.hex()}")
    
    # Base64 编码
    sig_base64 = base64.b64encode(signature).decode('utf-8')
    print(f"Base64 编码后的签名: {sig_base64}")
    
    # URL 编码（心知天气要求）
    sig = urllib.parse.quote(sig_base64, safe='')
    print(f"URL 编码后的签名: {sig}")
    
    return ts, sig

def test_api_call():
    """测试 API 调用"""
    print("\n" + "="*60)
    print("测试 2: API 调用验证")
    print("="*60)
    
    if not settings.WEATHER_API_UID or not settings.WEATHER_API_SECRET:
        print("❌ 错误: 未配置 API 密钥")
        return False
    
    uid = settings.WEATHER_API_UID
    secret = settings.WEATHER_API_SECRET
    
    # 生成签名
    ts, sig = generate_seniverse_signature(uid, secret)
    
    # 构建 API 请求参数
    api_url = "https://api.seniverse.com/v3/weather/daily.json"
    api_params = {
        "uid": uid,
        "sig": sig,
        "ts": ts,
        "location": "北京",
        "language": "zh-Hans",
        "unit": "c",
        "start": 0,
        "days": 3
    }
    
    print("\n" + "="*60)
    print("步骤 2: API 调用参数")
    print("="*60)
    print(f"API 端点: {api_url}")
    print(f"\n请求参数:")
    for key, value in api_params.items():
        if key == "sig":
            print(f"  {key}: {value[:30]}... (签名)")
        else:
            print(f"  {key}: {value}")
    
    # 发送请求
    print("\n" + "="*60)
    print("步骤 3: 发送 API 请求")
    print("="*60)
    
    # 方式1：手动构建 URL（避免 requests 对已编码的签名再次编码）
    print("\n--- 方式1: 手动构建 URL（签名已 URL 编码）---")
    try:
        # 手动构建 URL，签名已经 URL 编码，其他参数让 requests 编码
        url_params = {
            "uid": uid,
            "sig": sig,  # 签名已经 URL 编码
            "ts": ts,
            "location": "北京",
            "language": "zh-Hans",
            "unit": "c",
            "start": 0,
            "days": 3
        }
        
        # 手动构建查询字符串，但签名已经编码，其他参数需要编码
        query_parts = [f"uid={urllib.parse.quote(str(uid), safe='')}"]
        query_parts.append(f"sig={sig}")  # 签名已经编码，直接使用
        query_parts.append(f"ts={ts}")
        query_parts.append(f"location={urllib.parse.quote('北京', safe='')}")
        query_parts.append(f"language={urllib.parse.quote('zh-Hans', safe='')}")
        query_parts.append(f"unit=c")
        query_parts.append(f"start=0")
        query_parts.append(f"days=3")
        
        full_url = f"{api_url}?{'&'.join(query_parts)}"
        print(f"完整请求 URL (前200字符): {full_url[:200]}...")
        
        response = requests.get(full_url, timeout=10)
        
        print(f"HTTP 状态码: {response.status_code}")
        
        # 解析响应
        data = response.json()
        print(f"\n响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        
        # 检查响应状态
        if response.status_code == 200:
            if "results" in data and data["results"]:
                print("\n✓ API 调用成功！")
                return True
            else:
                print("\n⚠ API 返回成功，但数据格式异常")
                return False
        else:
            print(f"\n❌ API 调用失败 (HTTP {response.status_code})")
            if "status" in data:
                print(f"错误状态: {data.get('status')}")
            if "message" in data:
                print(f"错误信息: {data.get('message')}")
            
            # 如果签名验证失败，尝试方式2：直接使用私钥
            print("\n--- 方式2: 直接使用私钥（不使用签名）---")
            api_params_simple = {
                "key": secret,  # 直接使用私钥
                "location": "北京",
                "language": "zh-Hans",
                "unit": "c",
                "start": 0,
                "days": 3
            }
            print(f"请求参数: key=***, location=北京, ...")
            
            try:
                response2 = requests.get(api_url, params=api_params_simple, timeout=10)
                print(f"HTTP 状态码: {response2.status_code}")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if "results" in data2 and data2["results"]:
                        print("✓ 直接使用私钥方式成功！")
                        print("提示: 可以使用这种方式，但安全性较低")
                        return True
                    else:
                        print("⚠ 直接使用私钥方式返回数据格式异常")
                else:
                    data2 = response2.json() if response2.text else {}
                    print(f"❌ 直接使用私钥方式也失败: {data2.get('status', 'Unknown error')}")
            except Exception as e2:
                print(f"❌ 直接使用私钥方式出错: {e2}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主函数"""
    print("="*60)
    print("心知天气 API 测试工具")
    print("="*60)
    
    # 检查配置
    print("\n配置检查:")
    print(f"  WEATHER_API_UID: {'✓ 已配置' if settings.WEATHER_API_UID else '✗ 未配置'}")
    print(f"  WEATHER_API_SECRET: {'✓ 已配置' if settings.WEATHER_API_SECRET else '✗ 未配置'}")
    
    if not settings.WEATHER_API_UID or not settings.WEATHER_API_SECRET:
        print("\n❌ 请先配置 API 密钥")
        return
    
    # 测试签名生成
    test_api_call()

if __name__ == "__main__":
    main()