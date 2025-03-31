import os
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class DirReaderTool(Tool):
    """目录读取工具"""
    
    name = "dir_reader"  # 工具名称
    description = "读取一个文件夹下的全部文件的内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "dirs": {
            "type": "array",
            "description": "待读取的文件夹路径，格式为[dir1, dir2, ...]",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "results": {
            "type": "array",
            "description": "读取到的所有文件内容列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        dirs = inputs.get("dirs", [])
        
        try:
            # 读取所有指定目录中的文件
            results = []
            for dir in dirs:
                for file in os.listdir(dir):
                    with open(os.path.join(dir, file), 'r', encoding='utf-8') as f:
                        results.append(f.read())
            return results
        except Exception as e:
            raise Exception(f"文件夹内容读取出错！{str(e)}") 