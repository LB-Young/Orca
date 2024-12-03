class VariableToolPool:
    def __init__(self):
        self.variables = {}
        self.tools = {}
        self.agents = {}

    def add_agents(self, agent):
        for key, value in agent.items():
            self.agents[key] = value

    def add_tools(self, tools):
        for key, value in tools.items():
            self.tools[key] = value
    
    def init_agents(self, agents):
        self.agents = agents

    def init_tools(self, tools):
        self.tools = tools

    def get_agents(self):
        return self.agents
    
    def get_tools(self):
        return self.tools

    def get_agent(self, agent_name):
        return self.agents[agent_name]
    
    def get_tool(self, tool_name):
        return self.tools[tool_name]

    def init_variables(self, variables):
        self.variables = variables

    def add_variable(self, variables):
        for key, value in variables.items():
            self.variables[key] = value

    def remove_variable(self, variable):
        del self.variables[variable]

    def get_variables(self, variable_name=None):
        if variable_name is None:
            return self.variables
        else:
            return self.variables[variable_name]

    def update_variable(self, variable_name, new_value):
        self.variables[variable_name] = new_value
