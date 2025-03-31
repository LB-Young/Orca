import requests
import json
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class RetrivalFromDatabaseTool(Tool):
    """数据库检索工具"""
    
    name = "retrival_from_database"  # 工具名称
    description = "从数据库中检索数据"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "query": {
            "type": "string",
            "description": "查询语句",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "answer": {
            "type": "string",
            "description": "检索结果"
        }
    }
    
    # 工具属性
    properties = {}
    
    # API URL
    url = "http://127.0.0.1:8013/retrival"
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        query = inputs.get("query", "")
        
        # 参数校验
        if not query:
            raise Exception("查询语句不能为空")
        
        # 构建请求体
        request_body = {
            "file_path": "",
            "need_embedding": True,
            "db_name": "tmp",
            "db_type": "local",
            "query": query,
            "temperature": 1.0
        }
        
        # 发送请求并获取结果
        try:
            response = requests.post(url=self.url, data=json.dumps(obj=request_body))
            response.encoding = 'utf-8'
            ret = response.json()['answer']
            return ret
        except Exception as e:
            raise Exception(f"数据库检索失败: {str(e)}") 