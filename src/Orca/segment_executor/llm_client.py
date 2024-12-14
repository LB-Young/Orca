from openai import OpenAI
from together import Together
from groq import Groq



class LLMClient:
    def __init__(self, config_dict):
        self.default_client = OpenAI(api_key=config_dict["default_model_api_key"], base_url=config_dict['default_model_base_url'])
        self.default_llm_model_name = config_dict['default_llm_model_name']

        self.deepseek_client = OpenAI(api_key=config_dict["deepseek_chat_model_api_key"], base_url=config_dict['deepseek_chat_model_base_url'])
        self.deepseek_llm_model_name = config_dict['deepseek_chat_llm_model_name'].split(",")
        self.deepseek_code_llm_model_name = config_dict['deepseek_code_llm_model_name'].split(",")
        self.groq_client = Groq(api_key=config_dict["groq_api_key"])
        self.groq_llm_model_name = config_dict['groq_llm_model_name'].split(",")

        self.together_client = Together(api_key=config_dict["together_api_key"])
        self.together_llm_model_name = config_dict['together_llm_model_name'].split(",")

    async def get_client(self, prompt, model_name=None):
        self.client = self.default_client
        self.llm_model_name = self.default_llm_model_name
        return
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
        if self.client is None:
            self.client = self.default_client
            self.llm_model_name = self.default_llm_model_name

    async def generate_answer(self, prompt=None, messages=None, tools=None, model_name=None, stream=False):
        if messages is not None:
            prompt = messages[-1]['content']
        await self.get_client(prompt, model_name)
        # print("prompt:", prompt)
        # print("self.client:", self.client)
        # print("self.llm_model_name:", self.llm_model_name)
        if not stream:
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
        else:
            if messages is None:
                if tools is None:
                    response = self.client.chat.completions.create(
                        model=self.llm_model_name,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant"},
                            {"role": "user", "content": prompt},
                        ],
                        stream=True,
                    )
                    return response
                else:
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
                        stream=True,
                    )
                    return response
            

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
