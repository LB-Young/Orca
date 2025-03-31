from typing import Dict, Any, Iterator, Union
from .tool import Tool

class DictToMultilineStringTool(Tool):
    """字典转多行字符串工具"""
    
    name = "dict_to_multiline_string"  # 工具名称
    description = "把dict转换为多行的字符串"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "dict_data": {
            "type": "object",
            "description": "待转换的dict数据",
            "required": True
        },
        "indent": {
            "type": "integer",
            "description": "缩进空格数",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "string",
            "description": "转换后的多行字符串"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        dict_data = inputs.get("dict_data", {})
        indent = inputs.get("indent", 0)
        
        # 处理字典转换为多行字符串
        return await self._dict_to_multiline(dict_data, indent)
    
    async def _dict_to_multiline(self, dict_data, indent=0):
        # 递归处理字典转换为多行字符串的内部方法
        result = ""
        for key, value in dict_data.items():
            if isinstance(value, dict):  # 如果值是字典，递归处理
                inner = await self._dict_to_multiline(value, indent + 4)
                result += " " * indent + f"{key}:\n" + inner
            else:  # 否则直接添加键值对
                result += " " * indent + f"{key}: {value}\n"
        return result 