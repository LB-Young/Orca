import os
from openai import OpenAI
from typing import Dict, Any, Iterator, Union, List
from .tool import Tool
from Orca.tools.load_local_api_keys import load_local_api_keys

class MermaidAddPictureTool(Tool):
    """Mermaid流程图添加图片工具"""
    
    name = "mermaid_add_picture"  # 工具名称
    description = "在Mermaid流程图中添加图片"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "mermaid_string": {
            "type": "string",
            "description": "Mermaid格式的流程图字符串",
            "required": True
        },
        "pic_path": {
            "type": "string",
            "description": "图片路径，可以是单张图片或包含多张图片的文件夹",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "mermaid_string": {
            "type": "string",
            "description": "添加了图片节点后的Mermaid流程图字符串"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        mermaid_string = inputs.get("mermaid_string", "")
        pic_path = inputs.get("pic_path", "")
        
        # 参数校验
        if not mermaid_string:
            raise Exception("Mermaid字符串不能为空")
        if not pic_path:
            raise Exception("图片路径不能为空")
            
        try:
            pic_path = eval(pic_path)
        except:
            pass
        
        try:
            result = await self._add_picture_to_mermaid(mermaid_string, pic_path)
            return result
        except Exception as e:
            raise Exception(f"在Mermaid流程图中添加图片失败: {str(e)}")
    
    async def _add_picture_to_mermaid(self, mermaid_string, pic_path):
        """在Mermaid流程图中添加图片
        
        Args:
            mermaid_string: Mermaid格式的流程图字符串
            pic_path: 图片路径
            
        Returns:
            str: 添加了图片节点后的Mermaid流程图字符串
        """
        # 处理图片路径，获取所有图片列表
        if os.path.isdir(pic_path):
            tmp_pictures = os.listdir(pic_path)
            pictures = [os.path.join(pic_path, item) for item in tmp_pictures]
        elif os.path.isfile(pic_path):
            pictures = [pic_path]
        else:
            raise Exception(f"图片路径错误: {pic_path}")
            
        # 使用OpenAI API进行图片添加
        client = OpenAI(
            api_key=load_local_api_keys("aliyun"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        prompt = f"""
我有一个mermaid流程图：\n{mermaid_string}\n\n我想将本地的部分图片添加到流程图中，本地图片的路径是：\n{pictures}\n\n请把路径中相关的图片链接到对应的节点。\n图片节点的结构为：\nX --> table_n[image: "local_path_to_picture.png"]\n示例说明：表示X节点需要链接一张图片。\n\n结果直接返回添加了图片节点之后的完整的mermaid字符串。
"""
        completion = client.chat.completions.create(
            model="qwen-max-latest",  # 可按需更换模型名称
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ],
        )
        
        return completion.choices[0].message.content 