"""
工具调度器
"""
from typing import Dict, Any, List
import asyncio
from app.tools import TOOLS_REGISTRY

class ToolScheduler:
    """工具调度器，负责调用和管理工具"""
    
    def __init__(self):
        self.tools = TOOLS_REGISTRY
    
    async def call_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"工具 '{tool_name}' 不存在",
                "data": None
            }
        
        tool_info = self.tools[tool_name]
        tool_function = tool_info["function"]
        
        try:
            # 使用 asyncio.to_thread 在后台线程运行同步函数
            # 这样可以避免阻塞事件循环，同时正确处理取消操作
            result = await asyncio.to_thread(tool_function, parameters)
            return result
        except asyncio.CancelledError:
            # 正确处理取消操作
            return {
                "success": False,
                "error": "工具调用被取消",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"工具调用失败：{str(e)}",
                "data": None
            }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return [
            {
                "name": name,
                "description": info["description"],
                "required_params": info["required_params"],
                "optional_params": info.get("optional_params", [])
            }
            for name, info in self.tools.items()
        ]

