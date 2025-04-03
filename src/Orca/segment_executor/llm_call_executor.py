import logging
from pydantic import BaseModel
from typing import Optional, Dict, List, Union, Any
from Orca.segment_executor.llm_client import LLMClient
from Orca.utils.variable_replace import replace_variable

logger = logging.getLogger(__name__)

class ModelMessage(BaseModel):
    role: str
    content: str


class LLMCallExecutor:
    """LLM调用执行器，负责处理LLM相关的调用"""
    
    def __init__(self):
        self.all_states = None
        self.config_dict = None
        self.llm_client = None
        
    async def execute(self, 
                     messages: Union[str, List[Dict[str, str]]], 
                     all_states: Optional[Dict[str, Any]] = None,
                     stream: bool = False,
                     tools: Optional[List[Dict]] = None,
                     test_time_compute_type: Optional[str] = None,
                     **kwargs) -> Dict:
        """执行LLM调用
        
        Args:
            messages: 消息内容，可以是字符串或消息列表
            all_states: 全局状态
            stream: 是否使用流式输出
            tools: 可用的工具列表
            mode: 生成模式，可选值：chat/code/function
            **kwargs: 其他参数
            
        Returns:
            Dict: 包含执行结果和更新后的状态
        """
        # 初始化状态
        self.all_states = all_states or {}
        if not self.config_dict:
            if 'config' not in self.all_states:
                raise Exception("Config not found in all_states")
            self.config_dict = self.all_states['config'].get_configs()
            self.llm_client = LLMClient(config_dict=self.config_dict)
            
        # 处理消息格式
        processed_messages = []
        if isinstance(messages, str):
            # 替换变量
            messages = await replace_variable(messages, self.all_states)
            processed_messages = [{"role": "user", "content": messages}]
        else:
            memory = await messages.get_memory()
            # 处理消息列表
            for msg in memory:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # 如果是标准的消息字典格式
                    processed_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                elif isinstance(msg, ModelMessage):
                    # 如果是ModelMessage对象
                    processed_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                elif hasattr(msg, "role") and hasattr(msg, "content"):
                    # 如果是AgentMessage或其他具有role和content属性的对象
                    processed_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                else:
                    logger.warning(f"Skipping invalid message format: {msg}")
                    continue
            
        # 获取模型名称
        model = None
        if 'model' in kwargs:
            model = kwargs.pop('model')
        
        mode = "chat"
        if tools is not None:
            mode = "function"
        tmp_mode = await self.judge_prompt_type(processed_messages)
        if tmp_mode is not None:
            mode = tmp_mode

        # 调用LLM
        try:
            if test_time_compute_type == "BoN":
                pass
            elif test_time_compute_type in ["self-reflection", "self-refine"]:
                pass
            else:
                response = self.llm_client.generate_answer(
                    messages=processed_messages,  # 使用处理后的消息列表
                    model=model,
                    stream=stream,
                    tools=tools,
                    mode=mode,
                **kwargs
            )
            
            # 返回结果
            return {
                "execute_result": {
                    "result": response
                },
                "all_states": self.all_states
            }
            
        except Exception as e:
            logger.error(f"Error executing LLM call: {str(e)}")
            return {
                "execute_result": {
                    "result": f"Error: {str(e)}"
                },
                "all_states": self.all_states
            }

    async def judge_prompt_type(self, messages):
        for message in messages[::-1]:
            if message.get("role") == "user":
                content = message.get("content")
                if isinstance(content, str) and content.strip().startswith("CODE:"):
                    return "code"
                else:
                    return None
                break
        return None

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
