import asyncio


class ToolCallExecutor:
    def __init__(self):
        pass

    async def execute(self, function_object, function_input, all_states=None, stream=False):
        # 检查function_object是否是异步函数
        if 'condition_judge' in str(function_object) or "code_execute" in str(function_object):
            function_input['all_states'] = all_states
        if asyncio.iscoroutinefunction(function_object):
            try:
                tool_result = await function_object(**function_input)
            except:
                breakpoint()
                pass
        else:
            tool_result = function_object(**function_input)
        result = {
            "execute_result":{
                "result":tool_result,
            },
            "all_states":all_states
        }
        return result