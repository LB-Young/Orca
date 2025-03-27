import os
from pdf2image import convert_from_path
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class PDF2PicturesTool(Tool):
    """PDF转图片工具"""
    
    name = "pdf2pictures"  # 工具名称
    description = "将PDF文件转换为图片"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "pdf_path": {
            "type": "string",
            "description": "PDF文件路径",
            "required": True
        },
        "picture_save_path": {
            "type": "string",
            "description": "图片保存路径",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "string",
            "description": "转换结果信息"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        pdf_path = inputs.get("pdf_path", "")
        picture_save_path = inputs.get("picture_save_path", "")
        
        # 参数校验
        if not pdf_path:
            raise Exception("PDF路径不能为空")
        if not picture_save_path:
            raise Exception("图片保存路径不能为空")
        
        if not os.path.exists(pdf_path):
            raise Exception("PDF文件不存在")
        
        try:
            result = await self._convert_pdf_to_images(pdf_path, picture_save_path)
            return result
        except Exception as e:
            raise Exception(f"PDF转换图片失败: {str(e)}")
    
    async def _convert_pdf_to_images(self, pdf_path, picture_save_path):
        """将PDF文件转换为图片
        
        Args:
            pdf_path: PDF文件路径
            picture_save_path: 图片保存路径
            
        Returns:
            str: 转换结果信息
        """
        # 确保保存路径存在
        os.makedirs(picture_save_path, exist_ok=True)
        
        # 将PDF文件转换为图片
        images = convert_from_path(pdf_path)
        
        # 保存每一页为单独的图片
        for i, image in enumerate(images):
            image_path = os.path.join(picture_save_path, f'page_{i + 1}.png')
            image.save(image_path, 'PNG')
            
        return f"{pdf_path}文件已经转为图片，共{len(images)}页，图片保存在{picture_save_path}文件夹下。" 