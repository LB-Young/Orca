import subprocess
import sys
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class CmdExecuteTool(Tool):
    """命令行执行工具"""
    
    name = "cmd_execute"  # 工具名称
    description = "执行系统命令行，需要用户确认后执行"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "command": {
            "type": "string",
            "description": "要执行的命令字符串",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "object",
            "description": "命令执行结果，包含stdout、stderr、returncode和success字段"
        }
    }
    
    # 工具属性 - 这里可以定义需要用户确认的属性
    properties = {
        "confirm": {
            "type": "boolean",
            "description": "是否需要用户确认",
            "required": True,
            "default": True
        }
    }
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        command = inputs.get("command", "")
        need_confirm = properties.get("confirm", True)
        
        # 参数校验
        if not command or not isinstance(command, str):
            raise Exception("命令不能为空且必须是字符串")
        
        # 如果需要确认，显示命令并请求用户确认
        if need_confirm:
            print(f"即将执行命令: {command}")
            confirm = input("确认执行此命令? (y/n): ").strip().lower()
            
            # 如果用户未确认，取消执行
            if confirm != 'y' and confirm != 'yes':
                return "命令已取消执行"
        
        # 执行命令
        try:
            # 执行命令并获取输出
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            # 返回命令执行结果
            return {
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode,
                "success": process.returncode == 0
            }
            
        except Exception as e:
            raise Exception(f"命令执行失败: {str(e)}") 