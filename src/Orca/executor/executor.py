from Orca.executor.statements.statement_analysis import StatementsAnalysis

class Executor:
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variabletoolpool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        # sentetnce analysis 语义分析
        self.statement_analysis = StatementsAnalysis(variable_tool_pool=self.variabletoolpool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)

    async def execute(self, analysis_result, start_step=None, mode="c"):
        # Execute the command   
        # Return the result
        step_num = 0
        next_step_name = start_step
        # 如果非debug输入，则start_step为None，则从第一个步骤开始执行，否则从start_step开始执行
        if next_step_name is None:
            next_step_index = 0
        else:
            next_step_index = list(analysis_result.keys()).index(start_step)
        while step_num < 20:
            step_name = list(analysis_result.keys())[next_step_index]
            print(f"********************step_name: {step_name}********************")
            step_content = analysis_result[step_name]['content']
            step_exit = analysis_result[step_name]['exit']
            step_breakpoint = analysis_result[step_name]['breakpoint']
            if step_breakpoint:
                step_content = step_content.replace("(bp)", "")
            step_results, next_step_flag= await self.handle_step_content(step_content)
            print(f"step_results: {step_results}")

            if next_step_flag in list(analysis_result.keys()):
                next_step_name = next_step_flag
            else:
                if next_step_index < len(list(analysis_result.keys()))-1:
                    next_step_name = list(analysis_result.keys())[next_step_index+1]
                    next_step_index += 1
                else:
                    next_step_name = None

            # 记录memory and debuginfo
            step_memory_infos = {"name":step_name,
                                    "output": step_results}
            self.memories.add_memory(step_memory_infos)
            step_debug_info = step_memory_infos
            step_debug_info['input'] = step_content
            step_debug_info['next_step'] = next_step_name
            step_debug_info['variables'] = self.variabletoolpool.get_variables()
            step_debug_info['tools'] = self.variabletoolpool.get_tools()
            step_debug_info['agents'] = self.variabletoolpool.get_agents()
            self.debug_infos.add_debug_info(step_debug_info)

            # 中途退出或断点
            if step_exit or step_breakpoint or next_step_name is None or mode == "n":
                res_dict = {"output":step_results,
                            "msg":step_exit,
                            "debug_infos":self.debug_infos.get_debug_info()}
                if (step_breakpoint or mode == "n") and next_step_name is not None:
                    breakpoint_infos = {}
                    breakpoint_infos['variables'] = self.variabletoolpool.get_variables()
                    breakpoint_infos['tools'] = self.variabletoolpool.get_tools()
                    breakpoint_infos['agents'] = self.variabletoolpool.get_agents()
                    breakpoint_infos['memories'] = self.memories.get_memory()
                    breakpoint_infos['debug_infos'] = self.debug_infos.get_debug_info()
                    breakpoint_infos['next_step_name'] = next_step_name
                    breakpoint_infos["analysis_result"] = analysis_result
                    breakpoint_infos['config'] = self.config.get_config()
                    res_dict['breakpoint_infos'] = breakpoint_infos
                    del res_dict['debug_infos']
                return res_dict

            step_num += 1      

    async def handle_step_content(self, content):
        # deal with single step content
        step_results, next_step_flag = await self.statement_analysis.analyze(content)
        return step_results, next_step_flag


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