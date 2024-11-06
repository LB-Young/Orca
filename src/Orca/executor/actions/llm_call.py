import json
import re
from pydantic import BaseModel
from openai import OpenAI
from together import Together
from groq import Groq


class ModelMessage(BaseModel):
    role: str
    content: str


class LLMClient:
    def __init__(self, config_dict):
        self.default_client = OpenAI(api_key=config_dict["default_model_api_key"], base_url=config_dict['default_model_base_url'])
        self.default_llm_model_name = config_dict['default_llm_model_name']

        self.deepseek_client = OpenAI(api_key=config_dict["deepseek_chat_model_api_key"], base_url=config_dict['deepseek_chat_model_base_url'])
        self.deepseek_llm_model_name = config_dict['deepseek_chat_llm_model_name'].split(",")

        self.groq_client = Groq(api_key=config_dict["groq_api_key"])
        self.groq_llm_model_name = config_dict['groq_llm_model_name'].split(",")

        self.together_client = Together(api_key=config_dict["together_api_key"])
        self.together_llm_model_name = config_dict['together_llm_model_name'].split(",")

    async def get_client(self, prompt, model_name=None):
        if model_name is None:
            self.client = None
            self.llm_model_name = None
            if self.default_llm_model_name.lower() in prompt.lower():
                self.client = self.default_client
                self.llm_model_name = self.default_llm_model_name
            if self.client is None:
                for model_name in self.deepseek_llm_model_name:
                    if model_name.lower() in prompt.lower():
                        self.client = self.deepseek_client
                        self.llm_model_name = model_name
                        break
            if self.client is None:
                for model_name in self.groq_llm_model_name:
                    if model_name.lower() in prompt.lower():
                        self.client = self.groq_client
                        self.llm_model_name = model_name
                        break
            if self.client is None:
                for model_name in self.together_llm_model_name:
                    if model_name.lower() in prompt.lower():
                        self.client = self.together_client
                        self.llm_model_name = model_name
                        break
            if self.llm_model_name is None or self.client is None:
                all_models_name = self.deepseek_llm_model_name + self.groq_llm_model_name + self.together_llm_model_name
                model_choose_prompt = f"用户当前要求为：{prompt}\n用户已经配置好的模型是:{all_models_name}\n请在列表中选出用户想要使用的模型,如果没有符合条件的模型则使用{self.default_llm_model_name}。请直接返回选择的模型的名称，不要返回其它内容，格式如："+"{'model_name':''}"
                # print("model_choose_prompt:",model_choose_prompt)
                response = self.default_client.chat.completions.create(
                model=self.default_llm_model_name,
                messages=[
                    {"role": "system", "content": "你是一个专家助手。"},
                    {"role": "user", "content": model_choose_prompt},
                ],
                stream=False,
                )
                predict_model_name = response.choices[0].message.content
                # print("predict_model_name:",predict_model_name)
                if self.default_llm_model_name.lower() in predict_model_name.lower():
                    self.client = self.default_client
                    self.llm_model_name = self.default_llm_model_name
                if self.client is None:
                    for model_name in self.deepseek_llm_model_name:
                        if model_name.lower() in predict_model_name.lower():
                            self.client = self.deepseek_client
                            self.llm_model_name = model_name
                            break
                if self.client is None:
                    for model_name in self.groq_llm_model_name:
                        if model_name.lower() in predict_model_name.lower():
                            self.client = self.groq_client
                            self.llm_model_name = model_name
                            break
                if self.client is None:
                    for model_name in self.together_llm_model_name:
                        if model_name.lower() in predict_model_name.lower():
                            self.client = self.together_client
                            self.llm_model_name = model_name
                            break
        else:
            self.client = None
            self.llm_model_name = None
            for model_name in self.default_llm_model_name:
                if model_name.lower() in prompt.lower():
                    self.client = self.default_client
                    self.llm_model_name = model_name
                    break
            if self.client is None:
                for model_name in self.deepseek_llm_model_name:
                    if model_name.lower() in prompt.lower():
                        self.client = self.deepseek_client
                        self.llm_model_name = model_name
                        break
            if self.client is None:
                for model_name in self.groq_llm_model_name:
                    if model_name.lower() in prompt.lower():
                        self.client = self.groq_client
                        self.llm_model_name = model_name
                        break
            if self.client is None:
                for model_name in self.together_llm_model_name:
                    if model_name.lower() in prompt.lower():
                        self.client = self.together_client
                        self.llm_model_name = model_name
                        break

    async def generate_answer(self, prompt=None, messages=None, tools=None, model_name=None):
        if messages is not None:
            prompt = messages[-1]['content']
        await self.get_client(prompt, model_name)
        # print("prompt:", prompt)
        # print("self.client:", self.client)
        # print("self.llm_model_name:", self.llm_model_name)
        if messages is None:
            if tools is None:
                response = self.client.chat.completions.create(
                    model=self.llm_model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": prompt},
                    ],
                    stream=False,
                )
                return response.choices[0].message.content
        else:
            if tools is None:
                response = self.client.chat.completions.create(
                    model=self.llm_model_name,
                    messages=messages,
                    stream=False,
                )
                return response.choices[0].message.content
            

    async def choose_function(self, prompt, tools, model_name=None):
        await self.get_client(prompt, model_name)
        print("self.client:", self.client)
        print("self.llm_model_name:", self.llm_model_name)
        response = self.client.chat.completions.create(
            model=self.llm_model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False,
            tools=tools
        )
        function_name = response.choices[0].message.tool_calls[0].function.name
        function_params = response.choices[0].message.tool_calls[0].function.arguments
        return function_name, function_params
    

class LLMCall:
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variable_tool_pool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        self.config_dict = config.get_config()
        self.llm_client = LLMClient(config_dict=self.config_dict)

    async def execute(self, content):
        content = await self.replace_variable(content)
        response = await self.llm_client.generate_answer(content)
        return response, "next"

    async def replace_variable(self, prompt):
        prompt_variable_pattern = re.compile(r'\{.*?\}')
        matches = prompt_variable_pattern.findall(prompt)

        replace_dict = {}
        for match in matches:
            variable_name = match[1:-1]
            if variable_name.isdigit():
                memory = self.memories.get_memory(variable_name)[0]
                value = memory['output']
                replace_dict[match] = value
            else:
                value = self.variable_tool_pool.get_variables(variable_name)
                replace_dict[match] = value
        
        for key, value in replace_dict.items():
            prompt = prompt.replace(key, value)
        return prompt

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
