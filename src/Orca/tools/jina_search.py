import requests
from typing import Dict, Any, Iterator, Union, Optional
from .tool import Tool

class JinaSearchTool(Tool):
    """Jina搜索工具"""
    
    name = "jina_search"  # 工具名称
    description = "使用Jina Search API进行搜索"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "query": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        },
        "num": {
            "type": "integer",
            "description": "返回结果数量",
            "required": False
        },
        "page": {
            "type": "integer",
            "description": "页码",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "results": {
            "type": "string",
            "description": "搜索结果"
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
        num = inputs.get("num", 3)
        page = inputs.get("page", 1)
        
        # 参数校验
        if not query:
            raise Exception("搜索关键词不能为空")
        
        # 设置请求头
        headers = {
            "Authorization": "Bearer jina_96b4defcf63443a6bac47b925e172ab1dyLdulatxXX6jfMjmnTEafMXHxdp",
            "Content-Type": "application/json",
            "X-Retain-Images": "none",
            'X-Respond-With': 'no-content'
        }
        
        # 构建请求数据
        data = {
            "q": query,
            "gl": "US",
            "hl": "en",
            "num": str(num),
            "page": str(page)
        }
        
        # 发送请求并获取结果
        try:
            response = requests.post('https://s.jina.ai/', headers=headers, json=data)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jina搜索失败: {str(e)}") 