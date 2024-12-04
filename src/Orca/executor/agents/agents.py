import json
from Orca.executor.actions.llm_call import LLMCall
from Orca.executor.actions.function_call import FunctionCall
from Orca.executor.utils.variable_replace import replace_variable



class Agent:
    def __init__(self, roles=None, tools=None):
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
- 当需要调用工具的时候，你需要使用"=>$tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>$send_email: {subject: 'Hello', content: 'This is a test email'}"。

## Workflows：
- 分析用户问题，如果当前问题是其他角色擅长领域时触发对应的角色回答当前问题，如果没有与问题相关的角色则以自己的角色回答。
- 如果触发其他角色解答，使用以下符号进行触发：“=>@xxx:”，例如“=>@expert:”表示以专家角色开始发言,“=>@orca_agent:”表示不需要调用团队成员而是以自己的角色回答。
- 每一次当你触发了不同的角色之后，你需要切换到对应的角色进行回答。如“=>@law_expert:法律上的解释是……”
- 如果需要调用工具来处理，需要使用以下符号进行触发：“=>$tool_name: {key:value}”，例如“=>$send_email: {subject: 'Hello', content: 'This is a test email'}”。
- 每一次触发了不同的tool之后，你需要停止作答，等待用户调用对应的tool处理之后，将tool的结果重新组织语言后再继续作答，新的答案要接着“=>$tool_name”前面的最后一个字符继续生成结果，要保持结果通顺。
当前的问题为：{prompt}\n\n请回答这个问题。
"""
        self.roles_info = ""
        for key, value in roles.items():
            self.roles_info += f"@{key}: {value}\n"
        self.tools = {}
        self.tool_describe = []
        for key, value in tools.items():
            self.tools[key] = value["object"]
            self.tool_describe.append(f"{key}: {value['describe']}\n")
        self.role = self.role_format.replace(r"{roles}", self.roles_info).replace(r"{tools}", "".join(self.tool_describe))

        self.llmcall = LLMCall()
        self.functioncall = FunctionCall()

    async def execute(self, prompt, all_states=None, stream=False):
        prompt = await replace_variable(prompt, all_states)
        prompt = self.role.replace("{prompt}", prompt).strip()
        result = await self.llmcall.analysis(content=prompt, all_states=all_states, stream=stream, variable_replaced=True)
        if result['executed']:
            result = result['result']
        all_answer = ""
        tool_messages = ""
        tool_Flag = False
        for chunk in result:
            all_answer += chunk.choices[0].delta.content
            if tool_Flag:
                tool_messages += chunk.choices[0].delta.content
                continue
            if ":" in chunk.choices[0].delta.content and "=>$" in all_answer:
                tool_Flag = True
                tool_messages += chunk.choices[0].delta.content
                yield ": "
                continue
            yield chunk.choices[0].delta.content
        if tool_Flag:
            tool_messages = all_answer.split("=>$")[-1]
            result = await self.tool_run(tool_message=tool_messages, all_states=all_states)
            for item in str(result+"\n"):
                yield item
            query = prompt + "\n" + "已经执行内容:" + all_answer + "\n" + "工具执行结果:" + result
            async for item in self.execute(qeury=query):
                yield item

    async def tool_run(self, tool_message, all_states=None):
        analysis_result = await self.function_call.analysis(tool_message, all_states)
        if analysis_result['executed']:
            result = analysis_result['result']
            all_states = analysis_result['all_states']
        else:
            if analysis_result['analysis_result']['function_info']['type'] == "workflow_init":
                all_states = await self.execute(analysis_result['analysis_result']['function_info']['function_content'], all_states=all_states)
                result = all_states['variables_pool'].get_variable('final_result')
            else:
                raise Exception("Function type not supported")
        return result
    
