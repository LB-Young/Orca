import json
import re
from pydantic import BaseModel

from Orca.utils.variable_replace import replace_variable
from Orca.segment_executor.llm_client import LLMClient


class ModelMessage(BaseModel):
    role: str
    content: str


class LLMCallExecutor:
    def __init__(self):
        pass
        
    async def execute(self, content, all_states=None, stream=False, variable_replaced=False):
        self.all_states = all_states
        if all_states is None:
            raise Exception("All_states is None, and not init LLMCallExecutor")
        else:
            self.config_dict = all_states['config'].get_configs()
            self.llm_client = LLMClient(config_dict=self.config_dict)
        if not variable_replaced:
            content = await replace_variable(content, all_states)
        type = await self.judge_prompt_type(content)
        if type == "prompt":
            response = await self.llm_client.generate_answer(prompt=content, stream=stream)
        elif type == "code":
            response = await self.llm_client.generate_code(prompt=content, stream=stream)
        result = {
            "execute_result": {
                "result":response
            },
            "all_states":all_states
        }
        return result

    async def judge_prompt_type(self, prompt):
        if prompt.strip().startswith("CODE:"):
            return "code"
        else:
            return "prompt"



async def ut():
    llm = LLMClient()
    print(await llm.generate_answer("What is the weather like in New York City?"))
    print(await llm.choose_function("请提供一个由哈宇豪撰写的关于领域认知智能的文件，标签为政府行业和金融行业，一周内发布的视频", tools=[
            {
        "type": "function",
        "function": {
            "name": "search_file",
            "description": "查找文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "文件的标签，比如行业，产品等，多个标签用/分割",
                    },
                    "time": {
                        "type": "string",
                        "description": "文件的时间，比如一周内，一天内，三天内，半个月内，一个月内等",
                    },
                    "writer": {
                        "type": "string",
                        "description": "文件的作者，一个具体的人名，比如某某某",
                    },
                    "content": {
                        "type": "string",
                        "description": "文件的内容描述",
                    },
                    "type": {
                        "type": "string",
                        "description": "文件格式，比如pdf,word,excel,ppt,视频,音频，图片等",
                    }
                },
                "required": ["content"]
            },
        }
    }]))

if __name__ == "__main__":
    import asyncio
    asyncio.run(ut())
