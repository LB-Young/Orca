import re
import json
from Orca.executor.actions.llm_call import LLMClient
from Orca.executor.agents.agent_executor import AgentExecutor


class AgentCall:
    def __init__(self, variables_pool=None, config=None, tools_agents_pool=None, debug_infos=None):
        self.variables_pool = variables_pool
        self.tools_agents_pool = tools_agents_pool
        self.debug_infos = debug_infos
        self.config = config
        self.config_dict = config.get_configs()
        self.llm_client = LLMClient(self.config_dict)
        self.agent_executor = AgentExecutor(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)

    async def execute(self, prompt):
        # agents = []
        # user_agents = self.variable_tool_pool.get_agents()
        # default_agents = await self.agent_executor.get_agents()
        # for key, value in user_agents.items():
        #     if key in prompt:
        #         agents.append(value)
        #         break
        # for key, value in default_agents.items():
        #     if key in prompt:
        #         agents.append(value)
        #         break
        # if len(agents) == 0:
        #     agents = list(default_agents.values()) + list(user_agents.values())
        
        # # replace variable by the value
        # prompt = await self.replace_variable(prompt)
        # function_name, function_params = await self.llm_client.choose_function(prompt, agents)
        # function_params = json.loads(function_params)
        if "agent_call" in prompt:
            match = re.search(r"agent_call\('([\w.]+)',\s*(.*)\)\s*", prompt)
            function_name, function_params = match.groups()[0], match.groups()[1]
            result = await self.agent_executor.execute(function_name, function_params)
            return result, "next"
        else:
            result = await self.agent_executor.execute(None, prompt)
            return result, "next"
        
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
                value = self.variable_tool_pool.get_variable(variable_name)
                replace_dict[match] = value
        
        for key, value in replace_dict.items():
            prompt = prompt.replace(key, value)
        return prompt


