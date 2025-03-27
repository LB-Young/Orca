from openai import OpenAI
import os
import base64
from typing import Dict, Any, Iterator, Union
from .tool import Tool
from Orca.tools.load_local_api_keys import load_local_api_keys

class VLModelTool(Tool):
    """视觉语言模型工具"""
    
    name = "vl_model"  # 工具名称
    description = "提取图片中的文字内容或回答与图片相关的问题"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "pic_path": {
            "type": "string",
            "description": "图片路径，可以是单张图片或包含多张图片的文件夹",
            "required": True
        },
        "query": {
            "type": "string",
            "description": "对图片的提问或指令",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "content": {
            "type": "string",
            "description": "模型分析图片后的回复内容"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        pic_path = inputs.get("pic_path", "")
        query = inputs.get("query", "请详细分析这张图片中的内容")
        
        # 参数校验
        if not pic_path:
            raise Exception("图片路径不能为空")
        
        try:
            pic_path = eval(pic_path)
        except:
            pass
        
        try:
            result = await self._process_image(pic_path, query)
            return result
        except Exception as e:
            raise Exception(f"视觉语言模型处理失败: {str(e)}")
    
    async def _process_image(self, pic_path, query):
        """处理图片并调用视觉语言模型"""
        try:
            client = OpenAI(
                api_key=load_local_api_keys("aliyun"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            
            # 判断pic_path是文件还是文件夹
            if os.path.isfile(pic_path):
                base64_image = self._encode_image(pic_path)

                completion = client.chat.completions.create(
                    model="qwen-vl-max-latest",
                    messages=[
                        {
                            "role": "system",
                            "content": [{"type": "text", "text": "You are a helpful assistant."}]
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                                },
                                {"type": "text", "text": f"{query}"},
                            ],
                        }
                    ],
                )
                
                return completion.choices[0].message.content
            
            elif os.path.isdir(pic_path):
                # 遍历文件夹中的所有文件
                images_list = []
                for filename in os.listdir(pic_path):
                    if filename.split(".")[-1].lower() in ['jpg', 'png', 'jpeg']:
                        base64_image = self._encode_image(os.path.join(pic_path, filename))
                        images_list.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
                        if len(images_list) > 8:
                            break
                
                if not images_list:
                    raise Exception(f"在路径 {pic_path} 中没有找到有效的图片文件")
                
                completion = client.chat.completions.create(
                    model="qwen-vl-max-latest",
                    messages=[
                        {
                            "role": "system",
                            "content": [{"type": "text", "text": "You are a helpful assistant."}]
                        },
                        {
                            "role": "user",
                            "content": images_list + [
                                {"type": "text", "text": f"{query}"},
                            ],
                        }
                    ],
                )
                
                return completion.choices[0].message.content
            else:
                raise Exception("输入路径既不是文件也不是文件夹")

        except Exception as e:
            raise Exception(f"视觉语言模型处理失败: {str(e)}")
    
    def _encode_image(self, image_path):
        """将图片编码为base64格式"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8") 