class ToolsAgentsPool:
    def __init__(self):
        self.tools = {}
        self.agents = {}

    def add_agents(self, agents):
        for key, value in agents.items():
            self.agents[key] = value

    def add_tools(self, tools):
        for key, value in tools.items():
            tool_info = {
                "type": "function",
                "object": value
            }
            self.tools[key] = tool_info
    
    def init_agents(self, agents):
        self.agents = agents

    def init_tools(self, tools):
        for key, value in tools.items():
            tool_info = {
                "type": "function",
                "object": value
            }
            self.tools[key] = tool_info

    def get_agents(self):
        return self.agents
    
    def get_tools(self):
        return self.tools

    def get_agent(self, agent_name):
        return self.agents[agent_name]
    
    def get_tool(self, tool_name):
        return self.tools[tool_name]
