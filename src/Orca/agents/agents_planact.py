import json
import ast
from collections.abc import AsyncGenerator
from Orca.segment_executor import *


class PlanActAgent:
    def __init__(self, tools=None, system_prompt=None):

        self.system_prompt = system_prompt
        self.tools = []
        self.tools_mapping = {}
        self.tools_call = []
        for key, value in tools.items():
            tools_proerties = {}
            required_params = []
            for param_key, param_value in value["object"].inputs.items():
                tools_proerties[param_key] = {
                            "type": param_value['type'],
                            "description": param_value['description']
                    }
                if param_value['required']:
                    required_params.append(param_key)

            self.tools_mapping[key] = value["object"]

            self.tools.append({
                                "type": "function",
                                "function": {
                                    "name": value["object"].name,
                                    "description": value["object"].description,
                                    "parameters": {
                                        "type": "object",
                                        "properties": tools_proerties,
                                        "required": required_params
                                    },
                                }
                            })
        if self.system_prompt != "":
            self.system_prompt = [{"role":"user", "content":self.system_prompt}]
        if system_prompt is not None:
            self.system_prompt = []

        self.llm_call_executor = LLMCallExecutor()
        self.tool_call_executor = ToolCallExecutor()

    async def think(self, messages, all_states=None, stream=False):
        """思考阶段：调用 LLM 分析当前状态并决定下一步行动"""
        # 调用 LLM 获取下一步行动
        think_prompt = "请你根据当前问题处理的状态和目标，思考下一步应该做什么。你可以选择一个工具来完成任务，也可以选择自己回答。请注意：1、优先使用合适的工具来完成任务。2、工具调用只能使用function_call功能返回。"
        llm_response = await self.llm_call_executor.execute(
            messages=messages + [{"role": "user", "content": think_prompt}],
            all_states=all_states,
            stream=stream,
            tools=self.tools
        )
        
        # 从 LLM 响应中获取响应
        response = llm_response['execute_result']['result']
        
        # 如果是流式响应，直接生成每个块
        if isinstance(response, AsyncGenerator):
            complete_response = ""
            async for chunk in response:
                complete_response += chunk
                yield chunk, complete_response
        else:
            yield response, response

    async def act(self, action, all_states=None):
        """行动阶段：执行工具调用并返回结果"""
        try:
            tool_result = await self.tool_run(action, all_states)
            # 如果工具结果是异步生成器
            if isinstance(tool_result, AsyncGenerator):
                complete_result = ""
                async for chunk in tool_result:
                    complete_result += chunk
                    yield {
                        "success": True,
                        "result": chunk,
                        "complete_result": complete_result
                    }
            else:
                yield {
                    "success": True,
                    "result": tool_result,
                    "complete_result": tool_result
                }
        except Exception as e:
            yield {
                "success": False,
                "error": str(e),
                "complete_result": str(e)
            }

    async def plan(self, messages, all_states=None, stream=False):
        """规划阶段：调用 LLM 制定执行计划"""
        # 添加规划提示词
        plan_prompt = """请为当前任务制定一个详细的解决流程。
        要求：
        1. 将任务分解为具体的执行步骤
        2. 每个步骤都要清晰明确
        3. 以 JSON 数组格式返回，每个元素包含 step_number 和 description
        4. 格式示例：[{"step_number": 1, "description": "第一步描述"}, ...]
        
        请直接返回 JSON 格式的计划，不要包含其他内容。"""
        
        # 调用 LLM 获取执行计划
        llm_response = await self.llm_call_executor.execute(
            messages=messages + [{"role": "user", "content": plan_prompt}],
            all_states=all_states,
            stream=stream
        )
        
        # 从 LLM 响应中获取计划
        response = llm_response['execute_result']['result']
        
        # 如果是流式响应，拼接完整响应
        if isinstance(response, AsyncGenerator):
            complete_response = ""
            async for chunk in response:
                complete_response += chunk
            response = complete_response
        
        # 解析 JSON 格式的计划
        try:
            if response.startswith("```"):
                response = response.replace("json", "").replace("JSON```", "").replace("```", "").strip()
            plan_list = json.loads(response)
            return plan_list
        except:
            return [{"step_number": 1, "description": "无法解析计划，直接执行用户请求。"}]

    async def react(self, prompt, all_states=None, stream=False):
        """执行 React 循环，以生成器形式返回结果"""
        # 初始化消息列表
        messages = self.system_prompt + prompt
        
        # 最大尝试次数
        max_attempts = 25
        attempts = 0
        
        while attempts < max_attempts:
            # 思考阶段
            current_thought = ""
            async for thought_chunk, complete_thought in self.think(messages, all_states, stream):
                current_thought = complete_thought
                # 生成思考过程的每个块
                yield thought_chunk
            # 如果找到最终答案，生成结果并结束
            if "Final Answer:" in current_thought:
                final_answer = current_thought.split("Final Answer:", 1)[1].strip()
                yield final_answer
                break
            # 行动阶段
            current_result = None
            async for action_state in self.act(current_thought, all_states):
                if action_state["success"]:
                    # 生成行动结果
                    yield str(action_state["result"])
                    yield "\n"
                    current_result = action_state["complete_result"]
                else:
                    # 生成错误信息
                    yield f"Error: {action_state['error']}"
                    yield "\n"
                    current_result = action_state["complete_result"]
            
            # 更新消息历史
            messages.append({"role": "assistant", "content": current_thought})
            if current_result is not None:
                if isinstance(current_result, str) and current_result.startswith("Error:"):
                    messages[-1]["content"] += f"\nError executing tool: {current_result}"
                else:
                    messages[-1]["content"] += f"\nTool response: {current_result}"
            
            attempts += 1
        
        # 如果达到最大尝试次数，生成失败信息
        yield "Failed to complete the task within maximum attempts."

    async def step_react(self, step, messages, all_states=None, stream=False):
        """执行单个步骤的思考和行动过程"""
        # 添加当前步骤到消息历史
        step_prompt = f"当前执行到第 {step['step_number']} 步：{step['description']}。你可以选择一个工具来完成任务，也可以选择自己回答。请注意：1、优先使用合适的工具来完成任务。2、工具调用只能使用function_call功能返回。"
        step_messages = [{"role": "user", "content": step_prompt}]

        # 最大尝试次数
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            # 思考阶段
            current_thought = ""
            async for thought_chunk, complete_thought in self.think(messages+step_messages, all_states, stream):
                current_thought = complete_thought
                # 生成思考过程的每个块
                yield thought_chunk
            # 如果找到最终答案，生成结果并结束
            if "Final Answer:" in current_thought:
                final_answer = current_thought.split("Final Answer:", 1)[1].strip()
                yield final_answer
                break
            # 行动阶段
            current_result = None
            async for action_state in self.act(current_thought, all_states):
                if action_state["success"]:
                    # 生成行动结果
                    yield str(action_state["result"])
                    yield "\n"
                    current_result = action_state["complete_result"]
                else:
                    # 生成错误信息
                    yield f"Error: {action_state['error']}"
                    yield "\n"
                    current_result = action_state["complete_result"]
            
            # 更新消息历史
            step_messages.append({"role": "assistant", "content": current_thought})
            if current_result is not None:
                if isinstance(current_result, str) and current_result.startswith("Error:"):
                    step_messages[-1]["content"] += f"\nError executing tool: {current_result}"
                else:
                    step_messages[-1]["content"] += f"\nTool response: {current_result}"
            
            attempts += 1
        
        # 如果达到最大尝试次数，生成失败信息
        if attempts == max_attempts:
            yield "Failed to complete the task within maximum attempts."
        else:

            llm_response = await self.llm_call_executor.execute(
                messages=step_messages + [{"role": "user", "content": "请总结步骤{step['step_number']} ：{step['description']}的执行结果。"}],
                all_states=all_states,
                stream=stream
            )
            
            # 从 LLM 响应中获取响应
            response = llm_response['execute_result']['result']
            
            # 如果是流式响应，直接生成每个块
            if isinstance(response, AsyncGenerator):
                complete_response = ""
                async for chunk in response:
                    complete_response += chunk
                step_result = complete_response
            else:
                step_result = response

            yield f"第 {step['step_number']} 步：“{step['description']}”的执行结果为：{step_result}。"

    async def execute(self, prompt, all_states=None, stream=False):
        """执行带计划的任务"""
        # 初始化消息列表
        messages = self.system_prompt + prompt
        
        # 首先进行规划
        plan_list = await self.plan(messages, all_states, stream)
        yield "执行计划：\n" + "\n".join([f"{step['step_number']}. {step['description']}" for step in plan_list]) + "\n"
        
        if (not isinstance(plan_list, list)) or (not isinstance(plan_list[0], dict)) or ((len(plan_list) == 1) and (plan_list[0]['description'] == "无法解析计划，直接执行用户请求。")):
            # 如果无法解析计划，使用 react 模式执行
            async for result in self.react(prompt, all_states, stream):
                yield result
        else:
            # 对每个计划步骤进行执行    
            messages += [{"role": "assistant", "content": f"为解决上述问题我的执行计划如下：\n{'\n'.join([f'{step['step_number']}. {step['description']}' for step in plan_list])}"}]
            for step in plan_list:
                async for result in self.step_react(step, messages, all_states, stream):
                    yield result
                    messages.append({"role": "assistant", "content": result})
                

    async def tool_run(self, tool_message, all_states=None):
        function_name, function_params = tool_message.split(":", 1)
        function_params_json = await self.params_extract(function_params)
        if isinstance(function_params_json, str):
            return function_params_json
        execute_result = await self.tool_call_executor.execute(self.tools_mapping[function_name], function_params_json, all_states)
        result = execute_result['execute_result']['result']
        return result


    async def params_extract(self, params_content):
        stack = 0
        params_content = params_content.strip()
        if params_content[0] != "{":
            raise Exception("params_content extract error, can not be parsed to json")
        json_end = 0
        for index, char in enumerate(params_content):
            if char == "{":
                stack += 1
            elif char == "}":
                stack -= 1
            if stack == 0:
                json_end = index + 1
                break

        params_content = params_content[:json_end]

        success_paser = False
        try:
            params_extract = ast.literal_eval(params_content)
            success_paser = True
        except:
            pass
        try:
            if not success_paser:
                params_extract = json.loads(params_content.replace("'", '"'))
            success_paser = True
        except:
            pass
        try:
            if not success_paser:
                params_extract = json.loads(params_content.replace("'", '"'), strict=True)
            success_paser = True
        except:
            pass
        if not success_paser:
            return f"参数生成的格式错误，无法解析为正确的markdown格式：\n{params_content}"
        else:   
            return params_extract


