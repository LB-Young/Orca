from Orca.register.variables_pool import VariablesPool
from Orca.register.tools_agents_pool import ToolsAgentsPool
from Orca.debug.debug_info import DebugInfo
from Orca.register.config import Config
from Orca.executor import Executor
from Orca.agents.agents import Agent

class OrcaExecutor:
    def __init__(self):
        self.config = Config()
        self.debug_infos = DebugInfo()
        self.variables_pool = VariablesPool()
        self.tools_agents_pool = ToolsAgentsPool()

    def init_executor(self, init_parmas):
        for key, value in init_parmas.items():
            if key == "debug_infos":
                self.debug_infos.init_debug_info(debug_info=value)
            elif key == "variables":
                self.variables_pool.init_variables(variables=value)
            elif key == "tools":
                self.tools_agents_pool.init_tools(tools=value)
            elif key == "configs":
                self.config.init_config(configs=value)
            elif key == "agents":
                self.tools_agents_pool.init_agents(agents=value)
            elif key == "default_agent":
                if value['flag']:
                    roles = value['roles']
                    tools = init_parmas['tools']
                    default_agent = Agent(roles=roles, tools=tools)
                    default_agent_msg = {
                        "object": default_agent,
                        "describe": "这个是系统默认的专业agent，当用户没有指定回答的agent时，使用当前的agent回答。"
                    }
                    self.tools_agents_pool.add_agents(agents={"default_agent":default_agent_msg})
            else:
                pass

    async def execute(self, prompt, breakpoint_infos=None, mode="c"):
        if not breakpoint_infos:
            all_states = {
                "variables_pool":self.variables_pool, 
                "tools_agents_pool":self.tools_agents_pool, 
                "debug_infos":self.debug_infos,
                "config":self.config, 
            }
            executor = Executor()
            response = await executor.execute(prompt=prompt, all_states=all_states, mode="c")
            return response
        else:
            self.variables_pool.init_variables(variables=breakpoint_infos["variables"])
            self.tools_agents_pool.init_tools(tools=breakpoint_infos["tools"])
            self.tools_agents_pool.init_agents(agents=breakpoint_infos["agents"])
            self.debug_infos.init_debug_info(debug_info=breakpoint_infos["debug_infos"])
            self.config.init_config(configs=breakpoint_infos["configs"])
            all_states = {
                "variables_pool":self.variables_pool, 
                "tools_agents_pool":self.tools_agents_pool, 
                "debug_infos":self.debug_infos,
                "config":self.config, 
                "prompt_segments":breakpoint_infos['prompt_segments'],
            }
            executor = Executor()
            response = await executor.execute(prompt=prompt, all_states=all_states, mode=mode)
            return response

