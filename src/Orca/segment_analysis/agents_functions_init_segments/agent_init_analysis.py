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
        roles, tools, describe_content, system_prompt = await self.get_roles_tools(prompt_content, all_states)
        cur_agent = Agent(tools, system_prompt)
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

    async def get_roles_tools(self, prompt_content, all_states):
        prompt_content = prompt_content.strip().replace("@agent_init", "")
        if prompt_content.startswith("(") and prompt_content.endswith(")"):
            prompt_content = prompt_content[1:-1].strip()
        else:
            raise Exception(f"agent init failed! {prompt_content} is invalid")
        pattern = r'((roles)|(tools)|(describe)|(prompt)) *='
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
            if "roles" in key:
                all_key.append("roles")
            elif "tools" in key:
                all_key.append("tools")
            elif "describe" in key:
                all_key.append("describe")
            elif "prompt" in key:
                all_key.append("prompt")
        all_value = [prompt_content[all_end[i]:all_start[i + 1]].strip() for i in range(len(all_end))]

        roles_content = None
        tools_content = None
        describe_content = None
        prompt_content = None

        for cur_key, cur_value in zip(all_key, all_value):
            if cur_value.strip()[-1] == ",":
                cur_value = cur_value.strip()[:-1]
            if "roles" in cur_key:
                roles_content = cur_value
            elif "tools" in cur_key:
                tools_content = cur_value
            elif "describe" in cur_key:
                describe_content = cur_value
            elif "prompt" in cur_key:
                prompt_content = cur_value
        try:
            if roles_content is not None:
                roles = json.loads(roles_content)
            else:
                roles = {}
            
            if "tools" not in all_key:
                used_tools = {}
                return roles, used_tools, describe_content, prompt_content
            else:
                if "default" not in tools_content or len(tools_content)>3:
                    tools = eval(tools_content)
                    if isinstance(tools, dict):
                        return roles, tools, describe_content, prompt_content
                    elif isinstance(tools, list):
                        used_tools = {}
                        for key, value in all_states['tools_agents_pool'].get_tools().items():
                            if key in tools:
                                used_tools[key] = value
                        return roles, used_tools, describe_content, prompt_content
                else:
                    tools = all_states['tools_agents_pool'].get_tools()
                    return roles, tools, describe_content, prompt_content
        except:
            raise Exception(f"agent init failed! roles or tools is not json format! roles:{roles_content}, tools:{tools_content}")
