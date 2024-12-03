import re
from Orca.executor.statements.statement_analysis import StatementsAnalysis
from Orca.analysis.prompt_analysis import PromptAnalysis
from Orca.executor.statements.branch import BranchBlook
from Orca.executor.statements.circular import CircularBlock
from Orca.executor.actions.tool_call import ToolCall
from Orca.executor.actions.llm_call import LLMCall
from Orca.executor.actions.agent_call import AgentCall
from Orca.executor.actions.function_call import FunctionCall


class Executor:
    def __init__(self, all_states=None):
        pass

    async def execute(self, prompt, all_states=None, mode="c"):
        # parser prompt
        self.prompt_analysis = PromptAnalysis()
        prompt_segments = await self.prompt_analysis.analyze(prompt, all_states=all_states)
        print(prompt_segments)
        # Execute the commandx
        # Return the result
        for prompt_segment in prompt_segments:
            all_states = await self.segment_execute(prompt_segment=prompt_segment, all_states=all_states)
        return all_states

    async def segment_execute(self, prompt_segment, all_states=None):
        """
        prompt_segment:type，content，result_variable，all_next_prompt；
        ["prompt"、"function"、"FOR"、"IF"、"exit"、"bp"、"agent_init"、"function_init"]
        """
        pure_prompt, res_variable_name, variable_type, add_type = await self.prompt_segment_analysis(prompt_segment)
        if prompt_segment['type'] == "prompt":
            # 应该调用默认agent
            self.llm_call = LLMCall()
            result = await self.llm_call.execute(pure_prompt, all_states=all_states)
        elif prompt_segment['type'] == "function":
            # 直接调用函数
            self.function_call = FunctionCall()
            result = await self.function_call.execute(pure_prompt, all_states)
        elif prompt_segment['type'] == "agent_init":
            # 初始化agent
            pass
        elif prompt_segment['type'] == "function_init":
            pass
        elif prompt_segment['type'] == "FOR":
            # for循环处理逻辑
            self.circular_blook = CircularBlock()
            result, all_states = await self.circular_blook.execute(pure_prompt, all_states)
        elif prompt_segment['type'] == "IF":
            # 分支结构处理
            self.branch_blook = BranchBlook()
            result = await self.branch_blook.execute(pure_prompt, all_states)
        elif prompt_segment['type'] == "exit":
            result = prompt_segment['content']
            return
        elif prompt_segment['type'] == "bp":
            result = prompt_segment['content']

        if res_variable_name is not None:
            if add_type == "->":
                all_states['variables_pool'].add_variable(res_variable_name,result,variable_type)
            elif add_type == "->>":
                all_states['variables_pool'].add_variable_value(res_variable_name,result,variable_type)
            all_states['variables_pool'].add_variable("final_result", result, variable_type)
        print(result)
        return all_states
    
    async def prompt_segment_analysis(self, prompt_segment):
        # 匹配赋值指令的正则表达式
        pattern = r'^(.*?)(->|->>)\s*([a-zA-Z0-9_]+)(?:\((.*?)\))?$'
        
        content = prompt_segment['content']
        match = re.match(pattern, content.strip())
        
        if match:
            pure_prompt = match.group(1).strip()  # 执行指令
            add_type = match.group(2)  # -> 或 >>
            res_variable_name = match.group(3)  # 变量名
            variable_type = match.group(4) if match.group(4) else None  # 变量类型,可能为None
            
            return pure_prompt, res_variable_name, variable_type, add_type
        else:
            return content, None, None, None

    async def recursion_module(self, prompt, all_states=None):
        pass

async def ut():
    import json
    analysis_result_ifelse = """{'1': {'index': 0, 'content': 'query：{query}\n            写一首诗', 'exit': False, 'breakpoint': False}, '2': {'index': 1, 'content': "conditions:\n                conflag=llm_tagger({1},['田园诗','边塞诗','其它'])\n            if conflag=='田园诗':\n                goto  3\n      
        elif  conflag=='边塞诗':\n                goto  4\n            else:\n                goto  5", 'exit': False, 'breakpoint': False}, '3': {'index': 2, 'content': 'exit(msg="写了一首田园诗")', 'exit': True, 'breakpoint': False}, '4': {'index': 3, 'content': 'exit(msg="写了一首边
    塞诗")', 'exit': True, 'breakpoint': False}, '5': {'index': 4, 'content': 'exit(msg="写了一首其它类型的诗")', 'exit': True, 'breakpoint': False}}"""
    
    analysis_llm_params = """{'1': {'index': 0, 'content': '使用deepseek-chat模型写一首边塞诗', 'exit': False, 'breakpoint': False}, '2': {'index': 1, 'content': '用llama3写一首边塞诗', 'exit': False, 'breakpoint': False}, '3': {'index': 2, 'content': '用qwen2.5-72b对比{1}和{2}哪个好，并给出理由', 'exit': False, 'breakpoint': False}}"""

    analysis_result = json.loads(analysis_llm_params.replace("'", "\""))
    executor = Executor()
    result = await executor.execute(analysis_result)
    print(result)

if __name__ == '__main__':
    import asyncio
    asyncio.run(ut())