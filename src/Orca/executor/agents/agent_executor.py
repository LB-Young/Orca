from Orca.executor.agents.painter import Painter
from Orca.executor.agents.poet import Poet
from Orca.executor.agents.leader import Leader

class AgentExecutor:
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variable_tool_pool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        self.agents = []
        self.leader = Leader(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)
        
    
    async def get_agents(self,):
        return self.agents

    async def execute(self, agent_name, agent_instruct):
        if agent_name is not None:
            result = await self.agent_call_execute(agent_name, agent_instruct)
        else:
            result = await self.agent_prompt_execute(agent_instruct)
        return result

    async def agent_call_execute(self, agent_name, agent_instruct):
        if agent_name == "MultA":
            import requests
            from sseclient import SSEClient
            result = ""
            current_message = agent_instruct
            with requests.post(
                    "http://localhost:8000/chat",
                    json={"query": current_message},
                    stream=True,
                    headers={'Accept': 'text/event-stream'}
                ) as response:
                client = SSEClient(response)
                for event in client.events():
                    if event.data == "[DONE]":
                        break
                    cur_response_data = event.data.replace("\\n","\n")
                    result += cur_response_data
            return result

    async def agent_prompt_execute(self, agent_instruct):
        result = await self.leader.agent_run(agent_instruct)
        return result