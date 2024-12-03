from Orca.executor.statements.branch import BranchBlook
from Orca.executor.statements.circular import CircularBlock
from Orca.executor.actions.tool_call import ToolCall
from Orca.executor.actions.llm_call import LLMCall
from Orca.executor.actions.agent_call import AgentCall
class StatementsAnalysis:
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variable_tool_pool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        self.branch_blook = BranchBlook(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)
        self.circular_blook = CircularBlock(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)
        self.tool_call = ToolCall(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)
        self.llm_call = LLMCall(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)
        self.agent_call = AgentCall(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)

    async def analyze(self, content):
        # Analyze the statements
        # Return the analysis result
        content = content.strip()
        if content.startswith("for") or content.startswith("遍历"):
            step_results, next_step_flag = await self.circular_blook.execute(content)
        elif content.startswith("if") or "condition_judge" in content:
            step_results, next_step_flag = await self.branch_blook.execute(content)
        elif "tool_call" in content:
            step_results, next_step_flag = await self.tool_call.execute(content)
        elif "agent_call" in content:
            step_results, next_step_flag = await self.agent_call.execute(content)
        else:
            step_results, next_step_flag = await self.agent_call.execute(content)
            # step_results, next_step_flag = await self.llm_call.execute(content)
        return step_results, next_step_flag
