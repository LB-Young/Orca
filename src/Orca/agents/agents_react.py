import json
import ast
from collections.abc import AsyncGenerator
from Orca.segment_executor import *


class ReactAgent:
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
        think_prompt = "请你根据当前问题处理的状态和目标，思考下一步应该做什么。"
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

    async def execute(self, prompt, all_states=None, stream=False):
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


