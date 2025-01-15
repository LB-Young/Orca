import json
from Orca.segment_executor import *
from Orca.utils.variable_replace import replace_variable



class Agent:
    def __init__(self, roles=None, tools=None, system_prompt=None):
        self.role_format = """
# Role: 团队负责人

# Profile:
- version: 1.4
- language: 中文
- description: 你是一个团队负责人，但是你的团队只有你一个人，所以你要分饰多个角色解决对应的问题，但是你有很多的工具可以使用。

## Goals：
- 你需要分析用户的问题，决定由负责人的身份回答用户问题还是以团队其他人的角色来回答用户问题，Team Roles中的角色就是你可以扮演的团队的角色样例,除了示例角色之外你可以扮演任何其他角色。你还可以使用工具来处理问题，tools中的工具就是你可以使用的全部工具。

## Team Roles：
{roles}

## tools:
{tools}

## Constraints：
- 你必须清晰的理解问题和各个角色擅长的领域，并且熟练使用工具。
- 你需要将问题以最合适的角色回答，如果没有合适的角色则直接以自己的角色回答。
- 你必须使用“=>@xxx:”的格式来触发对应的角色。
- 你需要将问题拆分成详细的多个步骤，并且使用不同的角色回答。
- 当需要调用工具的时候，你需要使用"=>#tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>#send_email: {subject: 'Hello', content: 'This is a test email'}"。
- 调用工具的时候，工具后列出的参数都是必须参数，所有参数都需要被赋值不能有遗漏。

## Notes
- 注意：优先使用tool回答问题，只有在tool无法回答问题的时候才使用role。

## Workflows：
1、分析问题
    1.1、判断问题是否可以通过调用tool解决；如果可以，则调用tool解决（步骤2）。
    1.2、判断问题是否可以通过调用Roles中的角色解决；如果可以，则调用role解决（步骤3）。
    1.3、如果没有与问题相关的tool和role、则以自己的角色回答（步骤3）。
2、调用tool
    2.1、如果需要调用工具来处理，需要使用以下符号进行触发：“=>#tool_name: {key:value}”，例如“=>#send_email: {subject: 'Hello', content: 'This is a test email'}”。
    2.2、每一次触发了不同的tool之后，你需要停止作答，等待用户调用对应的tool处理之后，将tool的结果重新组织语言后再继续作答，新的答案要接着“=>#tool_name”前面的最后一个字符继续生成结果，要保持结果通顺。
3、调用role
    3.1、如果触发其他角色解答，使用以下符号进行触发：“=>@xxx:”，例如“=>@expert:”表示以专家角色开始发言,“=>@orca_agent:”表示不需要调用团队成员而是以自己的角色回答。
    3.2、每一次当你触发了不同的角色之后，你需要切换到对应的角色进行回答。如“=>@law_expert:法律上的解释是……”

{system_prompt}
{history_message}
当前的问题为：{prompt}\n。
"""
        if system_prompt is None:
            self.role_format = self.role_format.replace(r"{system_prompt}", "")
        else:
            self.role_format = self.role_format.replace(r"{system_prompt}", f"## JOB Description:\n {system_prompt}\n")
        self.roles_info = ""
        for key, value in roles.items():
            self.roles_info += f"@{key}: {value}\n"
        if len(self.roles_info) == 0:
            self.roles_info = "没有其他角色"
        self.tools = {}
        self.tool_describe = []
        for key, value in tools.items():
            self.tools[key] = value["object"]
            self.tool_describe.append(f"{key}: {value['describe']}\n")
        if len(self.tool_describe) == 0:
            self.tool_describe = "没有其他工具"
        self.role = self.role_format.replace(r"{roles}", self.roles_info).replace(r"{tools}", "".join(self.tool_describe))

        self.llm_call_executor = LLMCallExecutor()
        self.tool_call_executor = ToolCallExecutor()

    async def execute(self, prompt, all_states=None, stream=False):
        if isinstance(prompt, str):
            messages = eval(prompt)
        else:
            messages = prompt
        if len(messages) == 1:
            self.role = self.role.replace(r"{history_message}", "")
            query = messages[-1]["message"]
        else:
            history_messages = "## 历史对话信息为：\n" + str(messages[:-1]) + "\n"
            self.role = self.role.replace(r"{history_message}", history_messages)
            query = messages[-1]["message"]
        query = await replace_variable(prompt=query, all_states=all_states)
        cur_prompt = self.role.replace("{prompt}", query).strip()
        result = await self.llm_call_executor.execute(content=cur_prompt, all_states=all_states, stream=stream, variable_replaced=True)
        result = result['execute_result']['result']
        all_answer = ""
        tool_messages = ""
        tool_Flag = False
        for chunk in result:
            all_answer += chunk.choices[0].delta.content
            if tool_Flag:
                tool_messages += chunk.choices[0].delta.content
                continue
            if ":" in chunk.choices[0].delta.content and "=>#" in all_answer:
                tool_Flag = True
                tool_messages += chunk.choices[0].delta.content
                yield ": "
                continue
            yield chunk.choices[0].delta.content
        if tool_Flag:
            tool_messages = all_answer.split("=>#")[-1]
            result = await self.tool_run(tool_message=tool_messages, all_states=all_states)
            for item in str(result)+"\n":
                yield item
            new_query = query + "\n" + "已经执行内容:" + all_answer + "\n" + "工具执行结果:" + result
            new_messages = messages[:-1] + [{"role": "user", "message": new_query}]
            async for item in self.execute(prompt=new_messages, all_states=all_states, stream=stream):
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

