import requests
import os
from tqdm import tqdm
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class PDFDownloadTool(Tool):
    """PDF下载工具"""
    
    name = "pdf_download"  # 工具名称
    description = "从给定URL下载PDF文件并保存到指定目录"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "url": {
            "type": "string",
            "description": "PDF文件的URL",
            "required": True
        },
        "output_dir": {
            "type": "string",
            "description": "保存文件的目录",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "file_path": {
            "type": "string",
            "description": "保存的文件路径"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        url = inputs.get("url", "")
        output_dir = inputs.get("output_dir", ".")
        
        # 参数校验
        if not url:
            raise Exception("PDF文件URL不能为空")
        
        try:
            # 发送GET请求获取PDF文件
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            # 从URL中提取文件名，如果没有则使用默认名称
            filename = url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename = 'downloaded.pdf'

            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
                
            # 构建完整的文件保存路径
            file_path = os.path.join(output_dir, filename)

            # 获取文件大小（字节）
            file_size = int(response.headers.get('content-length', 0))

            # 使用tqdm创建进度条
            progress = tqdm(total=file_size, unit='iB', unit_scale=True)

            # 以二进制写入模式打开文件
            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    progress.update(size)

            progress.close()
            print(f"PDF文件已成功下载到: {file_path}")
            return {"file_path": file_path}

        except requests.exceptions.RequestException as e:
            raise Exception(f"下载PDF文件时发生错误: {str(e)}")
        except IOError as e:
            raise Exception(f"保存PDF文件时发生错误: {str(e)}") 