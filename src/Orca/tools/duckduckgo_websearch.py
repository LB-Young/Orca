from duckduckgo_search import DDGS
from typing import Dict, Any, Iterator, Union, List
from .tool import Tool

class DuckDuckGoWebSearchTool(Tool):
    """DuckDuckGo搜索工具"""
    
    name = "duckduckgo_websearch"  # 工具名称
    description = "使用DuckDuckGo搜索引擎进行网页搜索"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "query": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        },
        "num_results": {
            "type": "integer",
            "description": "搜索结果数量",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "results": {
            "type": "array",
            "description": "搜索结果列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        query = inputs.get("query", "")
        num_results = inputs.get("num_results", 5)
        
        # 参数校验
        if not query:
            raise Exception("搜索关键词不能为空")
        
        # 执行搜索
        results = DDGS().text(query, max_results=num_results)
        
        return results 