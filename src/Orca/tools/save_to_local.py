import json
import os
import aiofiles
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class SaveToLocalTool(Tool):
    """本地文件保存工具"""
    
    name = "save_to_local"  # 工具名称
    description = "将文本保存至本地"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "contents": {
            "type": "object",
            "description": "需要保存的内容",
            "required": True
        },
        "output_path": {
            "type": "string",
            "description": "输出路径",
            "required": True
        },
        "format": {
            "type": "string",
            "description": "文件格式，目前支持json",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "success": {
            "type": "boolean",
            "description": "保存是否成功"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        data = inputs.get("contents")
        file_path = inputs.get("output_path", "")
        format = inputs.get("format", "json")
        
        # 参数校验
        if not data or not file_path:
            raise Exception("无效的输入参数")
            
        if format not in ['json']:
            raise Exception("不支持的文件格式")
            
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if format == 'json':
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
                    await f.write(json_str)
                    
            return True
            
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}") 