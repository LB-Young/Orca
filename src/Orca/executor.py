import copy
from Orca.orca_language_analysis import PromptAnalysis
from Orca.segment_analysis import *
from Orca.segment_executor import *

class Executor:
    def __init__(self, all_states=None):
        pass

    async def execute(self, prompt, all_states=None, mode="c"):
        # parser prompt
        if "prompt_segments" not in all_states.keys():
            self.prompt_analysis = PromptAnalysis()
            prompt_segments = await self.prompt_analysis.analyze(prompt, all_states=all_states)
        else:
            prompt_segments = all_states['prompt_segments']
        # print("prompt解析后的列表:", prompt_segments)
        # print("-"*100)
        # Execute the commandx
        # Return the result
        execute_state = "prompt"
        for index, prompt_segment in enumerate(prompt_segments):
            all_states, execute_state = await self.segment_execute(prompt_segment=prompt_segment, all_states=all_states)
            if execute_state == "exit":
                break
            if  execute_state == "bp":
                all_states['prompt_segments'] = prompt_segments[index+1:]
                break
            if  mode == "n" and len(prompt_segments)>1:
                all_states['prompt_segments'] = prompt_segments[index+1:]
                execute_state = "bp"
                break
        return all_states, execute_state

    async def segment_execute(self, prompt_segment, all_states=None):
        execute_state = "normal"
        """
        prompt_segment:type，content，result_variable，all_next_prompt；
        ["prompt"、"function"、"FOR"、"IF"、"exit"、"bp"、"agent_init"、"function_init"]
        """
        pure_prompt, res_variable_name, variable_type, add_type = await self.prompt_segment_analysis(prompt_segment)
        # print("单句prompt分析结果：")
        print("当前执行语句：", pure_prompt, add_type, res_variable_name, variable_type)
        if prompt_segment['type'] == "prompt":
            if "default_agent" in all_states['tools_agents_pool'].get_agents().keys() and (not pure_prompt.strip().startswith("CODE")):
                # 应该调用默认agent
                self.function_call = FunctionCallAnalysis()
                pure_prompt = "@default_agent(" + pure_prompt + ")"
                analysis_result = await self.function_call.analysis(pure_prompt=pure_prompt, all_states=all_states)
                if analysis_result['analysis_result']['type'] == "agent":
                    self.agent_call_executor = AgentCallExecutor()
                    execute_result = await self.agent_call_executor.execute(agent_object=analysis_result['analysis_result']['object'], agent_input=analysis_result['analysis_result']['params'], all_states=analysis_result['all_states'], stream=True)
                    result = execute_result['execute_result']['result']
                    all_states = execute_result['all_states']
                else:
                    self.llm_call = LLMCallExecutor()
                    analysis_result = await self.llm_call.execute(pure_prompt, all_states=all_states)
                    if analysis_result['executed']:
                        all_states = analysis_result['all_states']
                        result = analysis_result['result']
                    else:
                        pass
            else:
                # prompt不用分析，直接运行
                if pure_prompt.strip().startswith("CODE"):
                    # 生成代码解决
                    pass
                else:
                    # 不生成代码直接解答
                    self.llm_call_executor = LLMCallExecutor()
                    execute_result = await self.llm_call_executor.execute(pure_prompt, all_states=all_states, stream=False)
                    all_states = execute_result['all_states']
                    result = execute_result['execute_result']['result']

        elif prompt_segment['type'] == "function":
            # 直接调用函数
            self.function_call = FunctionCallAnalysis()
            analysis_result = await self.function_call.analysis(pure_prompt, all_states)
            if analysis_result['analysis_result']['type'] == "workflow_init":
                # 递归执行
                all_states, execute_state = await self.execute(analysis_result['analysis_result']['object'], all_states=all_states)
                return_variable_name = analysis_result['analysis_result']['final_result_variable']
                return_variable_value = all_states['variables_pool'].get_variables(return_variable_name)
                return_variable_type = type(return_variable_value)
                all_states['copy_variables_pool'].add_variable(return_variable_name, return_variable_value, return_variable_type)
                all_states['variables_pool'] = copy.deepcopy(all_states['copy_variables_pool'])
                del all_states['copy_variables_pool'] 
                result = return_variable_value
            elif analysis_result['analysis_result']['type'] == "agent":
                # agent执行
                self.agent_call_executor = AgentCallExecutor()
                execute_result = await self.agent_call_executor.execute(agent_object=analysis_result['analysis_result']['object'], agent_input=analysis_result['analysis_result']['params'], all_states=analysis_result['all_states'], stream=True)
                result = execute_result['execute_result']['result']
                all_states = execute_result['all_states']
            elif analysis_result['analysis_result']['type'] == "function":
                # 普通函数
                self.tool_call_executor = ToolCallExecutor()
                execute_result = await self.tool_call_executor.execute(function_object=analysis_result['analysis_result']['object'], function_input=analysis_result['analysis_result']['params'], all_states=analysis_result['all_states'], stream=True)
                result = execute_result['execute_result']['result']
                all_states = execute_result['all_states']
            elif analysis_result['analysis_result']['type'] == "python_init":
                # python代码执行
                self.tool_call_executor = ToolCallExecutor()
                execute_result = await self.tool_call_executor.execute(function_object=analysis_result['analysis_result']['object'], function_input=analysis_result['analysis_result']['params'], all_states=analysis_result['all_states'], stream=True)
                result = execute_result['execute_result']['result']
                all_states = execute_result['all_states']
            else:
                raise Exception("Function type not supported")
        elif prompt_segment['type'] == "agent_init":
            # 初始化agent
            self.agent_init = AgentInitAnalysis()
            analysis_result = await self.agent_init.analysis(pure_prompt, all_states)
            all_states = analysis_result['all_states']
            all_states['tools_agents_pool'].add_agents(agents={res_variable_name.strip():analysis_result['analysis_result']['agent_object']})
            result = "agent 已经注册！"
                
        elif prompt_segment['type'] == "function_init":
            self.function_init = FunctionInitAnalysis()
            analysis_result = await self.function_init.analysis(pure_prompt, all_states)
            tool = analysis_result['analysis_result']['tool_object']
            all_states['tools_agents_pool'].add_tools(tool)
            result = "function 已经注册！"

        elif prompt_segment['type'] == "FOR":
            # for循环处理逻辑
            self.circular_blook = CircularAnalysis()
            analysis_result = await self.circular_blook.analysis(pure_prompt, all_states)
            iter_v = analysis_result['analysis_result']['iter_v']
            iter_list = analysis_result['analysis_result']['iter_list']
            for_content = analysis_result['analysis_result']['for_content']
            # print("提取后的for语句执行体：",for_content)
            for item in iter_list:
                all_states['variables_pool'].add_variable(iter_v.replace("$","").strip(), item)
                all_states, execute_state = await self.execute(for_content, all_states=all_states)
            all_states['variables_pool'].remove_variable(iter_v.replace("$","").strip())
            result = all_states['variables_pool'].get_variables('final_result')

        elif prompt_segment['type'] == "IF":
            # 分支结构处理
            self.branch_blook = BranchAnalysis()
            analysis_result = await self.branch_blook.analysis(pure_prompt, all_states)
            all_states, execute_state = await self.execute(analysis_result['analysis_result']['if_content'], all_states=all_states)
            result = all_states['variables_pool'].get_variables('final_result')

        elif prompt_segment['type'] == "exit":
            self.exit_block  = ExitAnalysis()
            analysis_result = await self.exit_block.analysis(pure_prompt, all_states)
            result = analysis_result['analysis_result']['result']
            all_states = analysis_result['all_states']
            all_states['variables_pool'].add_variable("final_result", result, "str")
            execute_state = "exit"

        elif prompt_segment['type'] == "bp":
            result = "进入bp"
            execute_state = "bp"

        if res_variable_name is not None:
            if add_type == "->":
                all_states['variables_pool'].add_variable(res_variable_name,result,variable_type)
            elif add_type == "->>":
                all_states['variables_pool'].add_variable_value(res_variable_name,result,variable_type)
            all_states['variables_pool'].add_variable("final_result", result, variable_type)
        print("当前步骤结果:", str(result))
        return all_states, execute_state
    
    async def prompt_segment_analysis(self, prompt_segment):
        """
        分析提示片段,提取执行指令、变量名、变量类型等信息
        """
        # 匹配赋值指令的正则表达式
        content = prompt_segment['content']
        # print("待分析的单句prompt:",content)
        if content.strip().startswith("FOR") or content.strip().startswith("IF"):
            prompt_variable = content.rsplit("END", 1)

            pure_prompt = prompt_variable[0] + "END"
            if len(prompt_variable[1].strip()) > 0:
                if "->>" in prompt_variable[1]:
                    add_type = "->>"
                    res_variable_name = prompt_variable[1].strip().split("->>")[1].strip()
                    if "(" in res_variable_name:
                        variable_type = res_variable_name.split("(")[1].split(")")[0]
                        res_variable_name = res_variable_name.split("(")[0]
                    else:
                        variable_type = None
                elif "->" in prompt_variable[1]:
                    add_type = "->"
                    res_variable_name = prompt_variable[1].strip().split("->")[1].strip()
                    if "(" in res_variable_name:
                        variable_type = res_variable_name.split("(")[1].split(")")[0]
                        res_variable_name = res_variable_name.split("(")[0]
                    else:
                        variable_type = None
                else:
                    res_variable_name, variable_type, add_type = None, None, None
                return pure_prompt, res_variable_name, variable_type, add_type
            else:
                return pure_prompt, None, None, None
        elif content.strip().startswith("```workflow"):
            pure_prompt = content.strip()
            # pure_prompt = content[content.index("def", 1):].strip()[:-3].strip()
            return pure_prompt, None, None, None
        else:
            if "->>" in content:
                add_type = "->>"
                prompt_variable = content.split("->>")
                pure_prompt = prompt_variable[0].strip()
                res_variable_name = prompt_variable[1].strip()
                if "(" in res_variable_name:
                    variable_type = res_variable_name.split("(")[1].split(")")[0]
                    res_variable_name = res_variable_name.split("(")[0]
                else:
                    variable_type = None
                return pure_prompt, res_variable_name, variable_type, add_type
            elif "->" in content:
                add_type = "->"
                prompt_variable = content.split("->")
                pure_prompt = prompt_variable[0].strip()
                res_variable_name = prompt_variable[1].strip()
                if "(" in res_variable_name:
                    variable_type = res_variable_name.split("(")[1].split(")")[0]
                    res_variable_name = res_variable_name.split("(")[0]
                else:
                    variable_type = "str"
                return pure_prompt, res_variable_name, variable_type, add_type
            else:
                return content, None, None, None


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