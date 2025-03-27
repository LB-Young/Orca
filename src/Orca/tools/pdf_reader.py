import os
import PyPDF2
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class PDFReaderTool(Tool):
    """PDF读取工具"""
    
    name = "pdf_reader"  # 工具名称
    description = "读取PDF文件的内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "file_path": {
            "type": "string",
            "description": "PDF文件的路径",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "content": {
            "type": "string",
            "description": "PDF文件内容"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        file_path = inputs.get("file_path", "")
        
        # 参数校验
        if not file_path:
            raise Exception("PDF文件路径不能为空")
        
        if not os.path.exists(file_path):
            raise Exception("PDF文件不存在")

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return {"content": text}
        except Exception as e:
            raise Exception(f"PDF读取失败: {str(e)}") 