import json
import ast
from Orca.segment_executor import *
from Orca.utils.variable_replace import replace_variable


class Agent:
    def __init__(self, tools=None, system_prompt=None):
    #     self.prompt_format = """{tools}
    # ## TOOLS USE
    # - 当需要调用工具的时候，你需要使用"=>#tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>#send_email: {subject: 'Hello', content: 'This is a test email'}"。
    # - 每一次触发了不同的tool之后，你需要停止作答，等待用户调用对应的tool处理之后，将tool的结果重新组织语言后再继续作答。
    # - 你不能一次输出两个工具调用的命令，如"=>#tool_name1: {key:value}, =>#tool_name2: {key:value}"，你需要先输出一个工具调用的命令，等待用户调用工具，结果返回后，再输出另一个工具调用的命令。
    # """
        self.prompt_format = """{tools}
    ## TOOLS USE
    - 当需要调用工具的时候，你需要使用"=>#tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>#send_email: {subject: 'Hello', content: 'This is a test email'}"。
    - 每一次回答，你只能调用一个工具，不能同时调用多个工具。
    """

        self.tools = {}
        self.tool_describe = []
        for key, value in tools.items():
            self.tools[key] = value["object"]
            self.tool_describe.append(f"{key}: {value['describe']}\n")
        if len(self.tool_describe) == 0:
            self.prompt_format = ""
        else:
            self.tool_describe = "".join(self.tool_describe)
            self.prompt_format = self.prompt_format.replace(r"{tools}", "TOOLS 使用说明\n你只能使用下列工具，不能捏造未列出的工具。\n\nTOOLS LIST:\n" + self.tool_describe + "\n\n")

        if self.prompt_format != "":
            self.system_prompt = [{"role":"user", "content":self.prompt_format}, {"role":"assistant", "content":"好的，我会严格遵循要求，触发一次工具调用之后立即停止作答，等待工具结果返回后继续。"}]
        if system_prompt is not None:
            self.system_prompt = [{"role":"user", "content":self.prompt_format}, {"role":"assistant", "content":"好的，我会严格遵循要求，触发一次工具调用之后立即停止作答，等待工具结果返回后继续。"}, {"role":"user", "content":system_prompt}]

        self.llm_call_executor = LLMCallExecutor()
        self.tool_call_executor = ToolCallExecutor()

    async def execute(self, prompt, all_states=None, stream=False):
        messages = self.system_prompt + prompt
        # print("\n\n---------messages:", messages, "\n\n\n")
        # breakpoint()
        result = await self.llm_call_executor.execute(messages=messages, all_states=all_states, stream=stream, variable_replaced=True)
        result = result['execute_result']['result']
        all_answer = ""
        tool_messages = ""
        tool_Flag = False
        for chunk in result:
            all_answer += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content
            if tool_Flag:
                tool_messages += chunk.choices[0].delta.content
                continue
            if ":" in chunk.choices[0].delta.content and "=>#" in all_answer:
                tool_Flag = True
                tool_messages += chunk.choices[0].delta.content
                # yield ": "
                continue

        if tool_Flag:
            tool_messages = all_answer.split("=>#")[-1]
            result = await self.tool_run(tool_message=tool_messages, all_states=all_states)
            yield "工具执行结果：```" + str(result) + "```\n\n"
            # for item in str(result)+"\n":
            #     yield item
            # if "请严格遵循用户最初的要求" in prompt[-1]["content"]:
            #     prompt = prompt[:-1]
            if len(str(result).strip()) > 0:
                new_prompt = prompt + [{"role": "assistant", "content": all_answer}, {"role": "user", "content": "工具执行结果：```" + str(result) + "```"}]
            else:
                new_prompt = prompt + [{"role": "assistant", "content": all_answer}, {"role": "user", "content": "工具执行结果为空，请重新处理。"}]
            async for item in self.execute(prompt=new_prompt, all_states=all_states, stream=stream):
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

        params_content = params_content[:json_end]

        success_paser = False
        try:
            params_extract = ast.literal_eval(params_content)
            success_paser = True
        except:
            pass
        try:
            if not success_paser:
                params_extract = json.loads(params_content.replace("'", '"'))
            success_paser = True
        except:
            pass
        try:
            if not success_paser:
                params_extract = json.loads(params_content.replace("'", '"'), strict=True)
            success_paser = True
        except:
            pass
        try:
            if not success_paser:
                params_extract = await self.re_params_extract(params_content=params_content[:json_end])
            success_paser = True
        except:
            pass
        if not success_paser:
            return f"参数生成的格式错误，无法解析为正确的markdown格式：\n{params_content}"
        else:   
            return params_extract

    async def tool_run(self, tool_message, all_states=None):
        function_name, function_params = tool_message.split(":", 1)
        function_params_json = await self.params_extract(function_params)
        if isinstance(function_params_json, str):
            return function_params_json
        
        execute_result = await self.tool_call_executor.execute(self.tools[function_name], function_params_json, all_states)
        result = execute_result['execute_result']['result']
        return result

