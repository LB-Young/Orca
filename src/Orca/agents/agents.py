import json
import ast
from Orca.segment_executor import *
from Orca.memory.agent_memory import AgentMemory
from Orca.message.agent_message import AgentMessage


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
        self.system_prompt = system_prompt
        self.tools = {}
        self.tool_describe = []
        # 初始化agent memory用于管理消息
        self.agent_memory = AgentMemory()
        
        for key, value in tools.items():
            self.tools[key] = value["object"]
            param_describe = ""
            for param_key, param_value in value['object'].inputs.items():
                param_describe += f"{param_key}: {param_value['description']}\n"
            self.tool_describe.append(f"{key}: {value['object'].description}\n" + "参数说明：" + param_describe + "\n")
            
        if len(self.tool_describe) == 0:
            self.prompt_format = ""
        else:
            self.tool_describe_content = ""
            for index, tool_des in enumerate(self.tool_describe):
                self.tool_describe_content += f"{index}. {tool_des}\n"
            self.prompt_format = self.prompt_format.replace(r"{tools}", "TOOLS 使用说明\n你只能使用下列工具，不能捏造未列出的工具。\n\nTOOLS LIST:\n" + self.tool_describe_content + "\n\n")

        self.has_init_memory = False
        self.llm_call_executor = LLMCallExecutor()
        self.tool_call_executor = ToolCallExecutor()

    async def init_memory(self):
        breakpoint()
        if self.prompt_format != "":
            self.system_prompt = [{"role":"user", "content":self.prompt_format}, {"role":"assistant", "content":"好的，我会严格遵循要求，触发一次工具调用之后立即停止作答，等待用户提供工具结果后继续。"}]
            # 将系统提示添加到memory中
            await self.agent_memory.add_memory(AgentMessage(
                role="user",
                content=self.prompt_format,
                message_type="user",
                message_from="system",
                message_to="assistant"
            ))
            await self.agent_memory.add_memory(AgentMessage(
                role="assistant",
                content="好的，我会严格遵循要求，触发一次工具调用之后立即停止作答，等待用户提供工具结果后继续。",
                message_type="assistant",
                message_from="assistant",
                message_to=""
            ))
            
        if self.system_prompt is not None:
            self.system_prompt = [{"role":"user", "content":self.prompt_format}, {"role":"assistant", "content":"好的，我会严格遵循要求，触发一次工具调用之后立即停止作答，等待用户提供工具结果后继续。"}, {"role":"user", "content":self.system_prompt}]
            # 将额外的系统提示添加到memory中
            await self.agent_memory.add_memory(AgentMessage(
                role="user",
                content=self.system_prompt,
                message_type="user",
                message_from="user",
                message_to=""
            ))

    async def execute(self, messages, all_states=None, stream=False, test_time_compute_type=None):
        if not self.has_init_memory:
            self.has_init_memory = True
            await self.init_memory()
        # 将用户提示添加到memory中
        self.agent_memory.add_memory(messages)


        if test_time_compute_type == "BoN":
            pass
        elif test_time_compute_type in ["self-reflection", "self-refine"]:
            pass
        else:
            result = await self.llm_call_executor.execute(messages=self.agent_memory, all_states=all_states, stream=stream)
            result = result['execute_result']['result']
            all_answer = ""
            tool_messages = ""
            tool_Flag = False
            async for chunk in result:
                all_answer += chunk
                yield chunk
                if tool_Flag:
                    tool_messages += chunk
                    continue
                if ":" in chunk and "=>#" in all_answer:
                    tool_Flag = True
                    tool_messages += chunk
                    continue


        # 将助手的回答添加到memory中
        await self.agent_memory.add_memory(AgentMessage(
            role="assistant",
            content=all_answer,
            message_type="assistant",
            message_from="assistant",
            message_to=""
        ))
        
        if tool_Flag:
            tool_messages = all_answer.split("=>#")[-1]
            result = await self.tool_run(tool_message=tool_messages, all_states=all_states)
            
            # 将工具调用结果添加到memory中
            await self.agent_memory.add_memory(AgentMessage(
                role="system",
                content=str(result),
                message_type="tool",
                message_from="tool",
                message_to=""
            ))
            
            yield "工具执行结果：```" + str(result) + "```\n\n"
            assistant_msg = AgentMessage(
                    role="assistant",
                    content=all_answer,
                    message_type="assistant",
                    message_from="assistant",
                    message_to="user"
                )
            if len(str(result).strip()) > 0:
                # 创建新的messages并添加到memory中
                user_msg = AgentMessage(
                    role="user",
                    content=f"工具执行结果：```{str(result)}```",
                    message_type="tool",
                    message_from="tool",
                    message_to="assistant"
                )
                new_messages = messages + [
                    assistant_msg,
                    user_msg
                ]
                await self.agent_memory.add_memory(assistant_msg)
                await self.agent_memory.add_memory(user_msg)
            else:
                # 创建新的messages并添加到memory中
                assistant_msg = AgentMessage(
                    role="assistant",
                    content=all_answer,
                    message_type="assistant",
                    message_from="assistant",
                    message_to="user"
                )
                user_msg = AgentMessage(
                    role="user",
                    content="工具执行结果为空，请重新处理。",
                    message_type="tool",
                    message_from="tool",
                    message_to="assistant"
                )
                new_messages = messages + [
                    assistant_msg,
                    user_msg
                ]
                await self.agent_memory.add_memory(assistant_msg)
                await self.agent_memory.add_memory(user_msg)
                
            async for item in self.execute(messages=new_messages, all_states=all_states, stream=stream):
                yield item

    async def re_params_extract(self, params_content):
        params_content = params_content.strip()
        if params_content[0] == "{":
            params_content = params_content[1:]
        if params_content[-1] == "}":
            params_content = params_content[:-1]
        params = {}
        for param in params_content.split(","):
            param = param.strip()
            key, value = param.split(":", 1)
            tmp_value = value.strip()
            if tmp_value[-1] in ["'", '"']:
                tmp_value = tmp_value[:-1]
            if tmp_value[0] in ["'", '"']:
                tmp_value = tmp_value[1:]
            params[key.strip()] = tmp_value.strip()
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

