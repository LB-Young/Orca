import re
import json
from Orca.agents.agents import Agent
from Orca.utils.variable_replace import replace_variable
import logging

logger = logging.getLogger(__name__)

class AgentInitAnalysis:
    def __init__(self):
        pass

    async def analysis(self, prompt_content, all_states=None):
        prompt_content = await replace_variable(prompt_content, all_states)
        res = await self.params_split(prompt_content, all_states)
        tools = res['tools']
        system_prompt = res['system_prompt']
        describe_content = res['describe']
        cur_agent = Agent(tools, system_prompt, all_states)
        agent_msg = {
            "object":cur_agent,
            "describe":describe_content
        }
        result = {
            "analysis_result":{
                "agent_object":agent_msg,
            },
            "all_states":all_states
        }
        return result

    async def params_split(self, prompt_content, all_states):
        contain_variables = ['tools', 'system_prompt', 'describe']
        res = {
            "tools":"",
            "system_prompt":"",
            "describe":""
        }
        if len(prompt_content.strip()) == 0:
            res['tools'] = {}
            return res
        
        prompt_content = prompt_content.strip().replace("@agent_init", "")
        if prompt_content.startswith("(") and prompt_content.endswith(")"):
            prompt_content = prompt_content[1:-1].strip()
        else:
            raise Exception(f"agent init failed! {prompt_content} is invalid")
        
        select_string = ""
        for item in contain_variables:
            select_string += "|(" + item + ")"
        select_string = select_string[1:]
        pattern = r'(' + select_string + ') *='
        match = re.search(pattern, prompt_content)
        match_res = {}
        past_start = 0
        cur_prompt = prompt_content
        while match is not None:
            cur_start, cur_end = match.span()
            cur_start, cur_end = cur_start+past_start, cur_end+past_start
            
            match_res[match.group()] = [cur_start, cur_end]
            past_start = cur_end
            cur_prompt = prompt_content[past_start:]
            logger.debug(cur_start, cur_end, match.group(), cur_prompt)
            match = re.search(pattern, cur_prompt)
            
        all_start = [value[0] for key, value in match_res.items()]
        all_start.append(len(prompt_content))
        all_end = [value[1] for key, value in match_res.items()]
        all_key = []
        for key, value in match_res.items():
            for contain_variable in contain_variables:
                if contain_variable in key:
                    all_key.append(contain_variable)

        all_value = [prompt_content[all_end[i]:all_start[i + 1]].strip() for i in range(len(all_end))]

        for cur_key, cur_value in zip(all_key, all_value):
            if cur_value.strip()[-1] == ",":
                cur_value = cur_value.strip()[:-1]
            for contain_variable in contain_variables:
                if contain_variable in cur_key:
                    cur_value = cur_value.strip()
                    if cur_value[0] == '"':
                        cur_value = cur_value[1:]
                    if cur_value[-1] == '"':
                        cur_value = cur_value[:-1]
                    res[contain_variable] = cur_value
        
        if len(res['tools'].strip()) == 0:
            res['tools'] = {}

        else:            
            if "tools" not in all_key:
                used_tools = {}
            else:
                if "default" not in res['tools']:
                    tools = eval(res['tools'])
                    if isinstance(tools, dict):
                        res['tools'] = tools
                    elif isinstance(tools, list):
                        used_tools = {}
                        for key, value in all_states['tools_agents_pool'].get_tools().items():
                            if key in tools:
                                used_tools[key] = value
                        res['tools'] = used_tools
                else:
                    tools = all_states['tools_agents_pool'].get_tools()
                    res['tools'] = tools
        return res
