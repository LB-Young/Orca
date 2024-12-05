import re
from Orca.executor.actions.llm_call import LLMClient
from Orca.executor.agents.poet import Poet
from Orca.executor.agents.expert import Expert

class Leader:
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variable_tool_pool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        self.llm_client = LLMClient(config_dict=self.config.get_configs())
        self.poet = Poet(self.llm_client)
        self.expert = Expert(self.llm_client)
        self.agents = {"poet": self.poet, "expert": self.expert, "self": self.llm_client}
        self.role = """
# Role: 团队负责人

# Profile:
- version: 1.4
- language: 中文
- description: 你是一个团队负责人，你的团队有不同领域的人才。

## Goals：
- 你需要分析用户的问题，决定由自己回答用户问题还是指定团队的其他人来回答用户问题。

## Team Member：
@ poet：诗人
@ expert：专家（擅长金融、法律）

## Constraints：
- 你必须清晰的理解问题，和团队成员擅长的领域。
- 你需要将问题指派给最合适的团队成员，如果没有成员擅长该领域则直接自己回答。
- 你必须使用“=>@xxx:”的格式来指派问题给团队成员。
- 你需要将问题拆分成详细的多个步骤，并且分别指派。

## Workflows：
- 分析用户问题，如果当前问题是团队成员擅长领域时指定成员回答当前问题，如果没有与问题相关的成员则自己回答。
- 如果指定团队成员解答，使用以下符号进行指示：“=>@xxx:”，例如“=>@expert:”表示由专家开始发言,“=>@self:”表示不需要调用团队成员而是自己回答。
- 每一次你只需要指定下一个小步骤应该由谁作答，并且指定这名成员需要完成的内容。如“=>@expert:解释一下白矮星是什么？”
- 如果前面对话内容已经处理了部分步骤，请接着处理下一个步骤，不需要重复处理之前的步骤。
- 如果当前问题已经处理完毕，则直接返回“=>@None:finished!”

当前的问题为：{prompt}\n\n已经完成的步骤为：“{finished_steps}”\n\n请指定下一步由谁作答以及需要完成的内容。
"""

    async def agent_run(self, qeury):
        all_result = ""
        finished_flag = "start"
        finished_steps = []
        times = 0
        while finished_flag != "None" and times < 10:
            times += 1
            if len(finished_steps) == 0:
                result_format = "当前问题还未完成任何步骤！"
            else:
                result_format = " - ".join(finished_steps)
            prompt = self.role.format(prompt=qeury, finished_steps=result_format)
            messages = [{"role": "system", "content": prompt}]
            result = await self.llm_client.generate_answer(messages=messages)
            print("agent_result:", result)
            match = re.search(r"=>@(.+?):(.+)", result)
            if match:
                agent_name = match.group(1)
                agent_job = match.group(2)
                if agent_name != "None":
                    if agent_name != "self":
                        agent_obj = self.agents[agent_name]
                        result = await agent_obj.execute(agent_job)
                    else:
                        result = await self.execute(agent_job)
                    # print("agent_result:", result)
                    all_result += result + "\n\n"
                    finished_steps.append(f"{agent_name}已经完成了{agent_job},结果为{result}")
                    finished_flag = agent_name
                else:
                    finished_flag = "None"
            else:
                continue
        return all_result
    
    async def execute(self, qeury):
        result = await self.llm_client.generate_answer([f'{"role": "user", "content": qeury}'])
        return result