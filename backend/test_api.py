"""
后端 API 测试脚本

使用方法：
1. 确保后端服务已启动（uvicorn app.main:app --reload）
2. 运行：python test_api.py
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(title: str, response: requests.Response):
    """打印响应结果"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(f"响应文本: {response.text}")

def test_health():
    """测试健康检查接口"""
    print("\n🔍 测试健康检查接口...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查", response)
    assert response.status_code == 200, "健康检查失败"
    assert response.json()["status"] == "ok", "状态不正确"
    print("✅ 健康检查测试通过")

def test_root():
    """测试根路径接口"""
    print("\n🔍 测试根路径接口...")
    response = requests.get(f"{BASE_URL}/")
    print_response("根路径", response)
    assert response.status_code == 200, "根路径访问失败"
    print("✅ 根路径测试通过")

def test_tools_status():
    """测试工具状态查询接口"""
    print("\n🔍 测试工具状态查询接口...")
    response = requests.get(f"{BASE_URL}/api/tools/status")
    print_response("工具状态", response)
    assert response.status_code == 200, "工具状态查询失败"
    data = response.json()
    assert data["code"] == 200, "返回码不正确"
    assert "tools" in data["data"], "缺少 tools 字段"
    print("✅ 工具状态查询测试通过")

def test_workflow_execute(user_input: str = "查北京天气"):
    """测试工作流执行接口"""
    print(f"\n🔍 测试工作流执行接口（输入：{user_input}）...")
    response = requests.post(
        f"{BASE_URL}/api/workflow/execute",
        json={
            "userInput": user_input,
            "conversationId": None
        },
        headers={"Content-Type": "application/json"}
    )
    print_response("工作流执行", response)
    assert response.status_code == 200, "工作流执行失败"
    data = response.json()
    assert data["code"] == 200, f"返回码不正确: {data.get('message')}"
    assert "data" in data, "缺少 data 字段"
    assert "taskId" in data["data"], "缺少 taskId 字段"
    assert "status" in data["data"], "缺少 status 字段"
    print("✅ 工作流执行测试通过")

def test_workflow_error():
    """测试工作流错误处理"""
    print("\n🔍 测试工作流错误处理...")
    # 测试空输入
    response = requests.post(
        f"{BASE_URL}/api/workflow/execute",
        json={"userInput": ""},
        headers={"Content-Type": "application/json"}
    )
    print_response("空输入测试", response)
    # 注意：当前实现可能不验证空输入，这里只是测试接口是否正常响应
    print("✅ 错误处理测试完成")

def run_all_tests():
    """运行所有测试"""
    print("="*50)
    print("开始测试后端 API")
    print("="*50)
    
    try:
        test_health()
        test_root()
        test_tools_status()
        test_workflow_execute("查北京天气")
        test_workflow_execute("查最近的 AI 新闻")
        test_workflow_error()
        
        print("\n" + "="*50)
        print("✅ 所有测试通过！")
        print("="*50)
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误：无法连接到后端服务")
        print("请确保后端服务已启动：")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")

if __name__ == "__main__":
    run_all_tests()


