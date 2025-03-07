from pydantic import BaseModel
from Orca.utils.variable_replace import replace_variable
from Orca.segment_executor.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)

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
            messages = [{"role": "user", "content": content}]
            response = await self.llm_client.generate_answer(messages=messages, stream=stream)
        elif type == "code":
            messages = [{"role":"system", "content":"你需要分析当前问题，并给出解决当前问题的python代码。"},{"role": "user", "content": content}]
            response = await self.llm_client.generate_answer(messages=messages, stream=stream)

        if stream:
            # 处理流式响应
            async def stream_processor():
                all_answer = ""
                all_think = ""
                try:
                    async for chunk in response:
                        all_answer += chunk["answer"]
                        all_think += chunk["think"]
                        yield {"content": chunk["answer"], "reasoning_content": chunk["think"]}
                except TypeError:
                    # 如果response不是异步迭代器，则按照非流式处理
                    if isinstance(response, dict) and "answer" in response and "think" in response:
                        all_answer = response["answer"]
                        all_think = response["think"]
                        yield {"content": all_answer, "reasoning_content": all_think}
                
                # 将最终结果存储到all_states中
                all_states['variables_pool'].add_variable("final_result", {"content": all_answer, "reasoning_content": all_think}, dict)
            
            return {
                "execute_result": {
                    "result": stream_processor()
                },
                "all_states": all_states
            }
        else:
            # 处理非流式响应
            all_states['variables_pool'].add_variable("final_result", {"content": response["answer"], "reasoning_content": response["think"]}, dict)
            
            result = {
                "execute_result": {
                    "result": response
                },
                "all_states": all_states
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
