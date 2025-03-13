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
        params = await self.get_roles_tools(prompt_content, all_states)
        system_prompt = params["system_prompt"]
        tools = params["tools"]
        model = params["model"]
        cur_agent = Agent(tools, system_prompt)
        agent_msg = {
            "object":cur_agent,
            "describe":system_prompt
        }
        result = {
            "analysis_result":{
                "agent_object":agent_msg,
            },
            "all_states":all_states
        }
        return result

    async def get_roles_tools(self, prompt_content, all_states):
        contain_variables = ["tools", "system_prompt", "model"]

        if len(prompt_content) == 0:
            res = {
                "tools":{},
                "system_prompt":"",
                "model":""
            }
            return res

        prompt_content = prompt_content.strip().replace("@agent_init", "")
        if prompt_content.startswith("(") and prompt_content.endswith(")"):
            prompt_content = prompt_content[1:-1].strip()
        else:
            raise Exception(f"agent init failed! {prompt_content} is invalid")
    
        select_content = ""
        for item in contain_variables:
            select_content += f"({item})|"
        select_content = select_content[:-1]

        pattern = rf'({select_content}) *='
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
            for item in contain_variables:
                if item in key:
                    all_key.append(item)
                else:
                    pass

        tmp_all_value = [prompt_content[all_end[i]:all_start[i + 1]].strip() for i in range(len(all_end))]
        all_value = []
        for item in tmp_all_value:
            item = item.strip()
            if len(item) == 0:
                continue
            else:
                if item[-1] == ",":
                    item = item[:-1]
            if item[0] == '"':
                item = item[1:]
            if item[-1] == '"':
                item = item[:-1]
            all_value.append(item)

        res = {
            "tools":"",
            "system_prompt":"",
            "model":""
        }

        for cur_key, cur_value in zip(all_key, all_value):
            if len(cur_value.strip()) == 0:
                continue
            for contain_variable in contain_variables:
                if contain_variable in cur_key:
                    res[contain_variable] = cur_value
                else:
                    pass

        if len(res["tools"].strip()) == 0:
            res["tools"] = {}
        else:
            if "default" not in res["tools"]:
                tools = eval(res["tools"])
                if isinstance(tools, dict):
                    res["tools"] = tools
                elif isinstance(tools, list):
                    used_tools = {}
                    for key, value in all_states['tools_agents_pool'].get_tools().items():
                        if key in tools:
                            used_tools[key] = value
                    res["tools"] = used_tools
                else:
                    raise Exception(f"agent init failed! tools is not json format! tools:{res['tools']}")
            else:
                res["tools"] = all_states['tools_agents_pool'].get_tools()

        return res
