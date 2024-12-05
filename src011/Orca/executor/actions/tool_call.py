import re
import json
from Orca.executor.actions.llm_call import LLMClient
from Orca.executor.tool_box.tool_executor import ToolExecutor


class ToolCall():
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variable_tool_pool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        self.config_dict = config.get_configs()
        self.llm_client = LLMClient(self.config_dict)
        self.tool_executor = ToolExecutor()

    async def execute(self, prompt):
        tools = []
        user_tools = self.variable_tool_pool.get_tools()
        default_tools = self.tool_executor.get_tools()
        for key, value in user_tools.items():
            if key in prompt:
                tools.append(value)
                break
        for key, value in default_tools.items():
            if key in prompt:
                tools.append(value)
                break
        if len(tools) == 0:
            tools = list(default_tools.values()) + list(user_tools.values())
        
        # replace variable by the value
        prompt = await self.replace_variable(prompt)
        function_name, function_params = await self.llm_client.choose_function(prompt, tools)
        function_params = json.loads(function_params)
        result = await self.tool_executor.execute(function_name, function_params)
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
