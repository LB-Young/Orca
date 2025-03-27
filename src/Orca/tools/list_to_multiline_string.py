from typing import Dict, Any, Iterator, Union, List
from .tool import Tool
from .dict_to_multiline_string import DictToMultilineStringTool

class ListToMultilineStringTool(Tool):
    """列表转多行字符串工具"""
    
    name = "list_to_multiline_string"  # 工具名称
    description = "把list转换为多行的字符串"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "list_data": {
            "type": "array",
            "description": "待转换的list数据",
            "required": True
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
    
    def __init__(self):
        # 初始化时创建一个字典转换工具实例，用于处理嵌套字典
        self.dict_tool = DictToMultilineStringTool()
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        list_data = inputs.get("list_data", [])
        
        # 处理列表转换为多行字符串
        return await self._list_to_multiline(list_data)
    
    async def _list_to_multiline(self, list_data: List) -> str:
        # 递归处理列表转换为多行字符串的内部方法
        result = ""
        for item in list_data:
            if isinstance(item, list):
                # 递归处理嵌套列表
                result += await self._list_to_multiline(item) + "\n"
            elif isinstance(item, dict):
                # 使用字典转换工具处理嵌套字典
                dict_inputs = {"dict_data": item, "indent": 0}
                result += await self.dict_tool.run(dict_inputs, {}) + "\n"
            else:
                # 直接转换其他类型
                result += str(item) + "\n"
        return result 