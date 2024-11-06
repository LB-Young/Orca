from Orca.analysis.prompt_analysis import PromptAnalysis
from Orca.variables.variable_tool_pool import VariableToolPool
from Orca.memory.memory import Memory
from Orca.debug.debug_info import DebugInfo
from Orca.config import Config
from Orca.executor.executor import Executor

class OrcaExecutor:
    def __init__(self):
        self.config = Config()
        self.memories = Memory()
        self.debug_infos = DebugInfo()
        self.variable_tool_pool = VariableToolPool()
    
    def init_executor(self, init_parmas):
        for key, value in init_parmas.items():
            if key == "memories":
                self.memories.init_memory(memory=value)
            elif key == "debug_infos":
                self.debug_infos.init_debug_info(debug_info=value)
            elif key == "variables":
                self.variable_tool_pool.init_variables(variables=value)
            elif key == "tools":
                self.variable_tool_pool.init_tools(tools=value)
            elif key == "config":
                self.config.init_config(configs=value)
            elif key == "agents":
                self.variable_tool_pool.init_agents(agents=value)
            else:
                pass

    async def execute(self, prompt, breakpoint_infos=None, mode="c"):
        if not breakpoint_infos:
            # prompt analysis split prompt into multi steps
            prompt_analysis = PromptAnalysis(prompt=prompt)
            analysis_result = await prompt_analysis.analyze()
            executor = Executor(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)
            response = await executor.execute(analysis_result=analysis_result, start_step=None, mode="c")
            return response
        else:
            self.variable_tool_pool.init_variables(variables=breakpoint_infos["variables"])
            self.variable_tool_pool.init_tools(tools=breakpoint_infos["tools"])
            self.variable_tool_pool.init_agents(agents=breakpoint_infos["agents"])
            self.memories.init_memory(memory=breakpoint_infos["memories"])
            self.debug_infos.init_debug_info(debug_info=breakpoint_infos["debug_infos"])
            self.config.init_config(configs=breakpoint_infos["configs"])
            self.start_step = breakpoint_infos["next_step_name"]
            executor = Executor(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)
            response = await executor.execute(analysis_result=breakpoint_infos["analysis_result"], start_step=self.start_step, mode=mode)
            return response

