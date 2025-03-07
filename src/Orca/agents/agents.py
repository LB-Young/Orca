import json
import copy
from Orca.segment_executor import *
from Orca.utils.variable_replace import replace_variable
from Orca.segment_executor.llm_client import LLMClient


class Agent:
    def __init__(self, tools=None, system_prompt="", all_states=None):
        self.role_format = """
## Goals：
- 你需要分析用户的问题，决定自己回答问题还是使用工具来处理，tools中列出的工具就是你可以使用的全部工具。

## tools:
{tools}

## tools use Constraints：
- 你必须清晰的理解问题并且熟练使用工具。
- 当需要调用工具的时候，你需要使用"=>#tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>#send_email: {subject: 'Hello', content: 'This is a test email'}"。
- 调用工具的时候，工具后列出的参数都是必须参数，所有参数都需要被赋值不能有遗漏。
- 每一次触发了tool调用之后，你需要暂停作答，并等待工具调用的结果。

{system_prompt}
"""     
        if len(tools) == 0:
            self.role_format = """{system_prompt}"""

        self.tools = {}
        self.tool_describe = []
        for key, value in tools.items():
            self.tools[key] = value["object"]
            self.tool_describe.append(f"{key}: {value['describe']}\n")
        self.role = self.role_format.replace(r"{tools}", "".join(self.tool_describe))

        if len(system_prompt) == 0:
            self.role = self.role.replace(r"{system_prompt}", "")
        else:
            self.role = self.role.replace(r"{system_prompt}", f"## User Demands:\n {system_prompt}\n")

        self.system_messages = [{"role":"system", "content":self.role}]  
        config_dict = all_states['config'].get_configs()
        self.llm_client = LLMClient(config_dict=config_dict)
        self.tool_call_executor = ToolCallExecutor()

    async def execute(self, messages, all_states=None, stream=False):

        full_messages = self.system_messages + messages
        # print(full_messages)

        result = await self.llm_client.generate_answer(messages=full_messages, stream=stream)

        all_answer = ""
        all_think = ""
        tool_Flag = False
        # for chunk in result:
        #     all_think += chunk.choices[0].delta.reasoning_content
        #     all_answer += chunk.choices[0].delta.content
        #     if tool_Flag:
        #         continue
        #     if ":" in chunk.choices[0].delta.content and "=>#" in all_answer:
        #         tool_Flag = True
        #         yield {"content": ": ", "reasoning_content": ""}
        #         continue
        #     yield {"content": chunk.choices[0].delta.content, "reasoning_content": chunk.choices[0].delta.reasoning_content}

        for chunk in result.iter_lines():
            try:
                tmp_chunk = json.loads(chunk.decode('utf-8').replace("data: ", ""), strict=True)
            except:
                continue
            # print("--->>", tmp_chunk['choices'][0]['delta'])
            if "choices" not in tmp_chunk:
                continue
            content = tmp_chunk['choices'][0]['delta']['content']
            reasoning_content = tmp_chunk['choices'][0]['delta']['reasoning_content']
            if content is None:
                content = ""
            if reasoning_content is None:
                reasoning_content = ""
            all_think += reasoning_content
            all_answer += content
            if tool_Flag:
                continue
            if ":" in content and "=>#" in all_answer:
                tool_Flag = True
                yield {"content": ": ", "reasoning_content": ""}
                continue
            # print("---->>", {"content": content, "reasoning_content": reasoning_content})
            yield {"content": content, "reasoning_content": reasoning_content}

        if tool_Flag:
            tool_messages = all_answer.split("=>#")[-1]
            result = await self.tool_run(tool_message=tool_messages, all_states=all_states)
            yield {"content": str(result)+"\n", "reasoning_content": ""}
            # for item in str(result)+"\n":
            #     yield {"content": item, "reasoning_content": ""}

            new_messages = messages + [{"role": "assistant", "content": all_answer + "工具结果为：```\n" + result + "\n```"}, {"role":"user", "content":"请你接着上一次的结果继续回答。"}]
            async for item in self.execute(messages=new_messages, all_states=all_states, stream=stream):
                yield item

    async def re_params_extract(self, params_content):
        params_content = params_content.strip()
        params = {}
        for param in params_content.split(","):
            param = param.strip()
            key, value = param.split(":", 1)
            params[key.strip()] = value.strip()
        return params

    async def params_extract(self, params_content):
        stack = 0
        params_content = params_content.strip()
        if params_content[0] != "{":
            raise Exception("params_content extract error, can not be parsed to json")
        json_end = 0
        for index, char in enumerate(params_content):
            if char == "{":
                stack += 1
            elif char == "}":
                stack -= 1
            if stack == 0:
                json_end = index + 1
                break
        try:
            return json.loads(params_content[:json_end].replace("'", '"'))
        except:
            re_extracted_params = await self.re_params_extract(params_content=params_content[:json_end])
            return re_extracted_params

    async def tool_run(self, tool_message, all_states=None):
        function_name, function_params = tool_message.split(":", 1)
        function_params_json = await self.params_extract(function_params)
        execute_result = await self.tool_call_executor.execute(self.tools[function_name], function_params_json, all_states)
        result = execute_result['execute_result']['result']
        return result

