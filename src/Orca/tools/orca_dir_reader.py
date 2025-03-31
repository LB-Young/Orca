import os
from typing import Dict, Any, Iterator, Union, List
from .tool import Tool

class OrcaDirReaderTool(Tool):
    """Orca目录读取工具"""
    
    name = "orca_dir_reader"  # 工具名称
    description = "读取一个文件夹下的全部文件的内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "dirs": {
            "type": "array",
            "description": "待读取的文件夹路径列表",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "contents": {
            "type": "array",
            "description": "读取到的文件内容列表"
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
        
        # 参数校验
        if not dirs or not isinstance(dirs, list):
            raise Exception("文件夹路径列表不能为空且必须是列表")
        
        try:
            results = []
            for dir_path in dirs:
                if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                    raise Exception(f"路径 {dir_path} 不存在或不是目录")
                    
                for file in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                results.append(f.read())
                        except UnicodeDecodeError:
                            # 尝试其他编码
                            with open(file_path, 'r', encoding='latin-1') as f:
                                results.append(f.read())
            
            return {"contents": results}
        except Exception as e:
            raise Exception(f"读取文件夹内容失败: {str(e)}") 