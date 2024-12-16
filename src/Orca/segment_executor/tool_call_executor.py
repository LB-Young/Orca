import asyncio


class ToolCallExecutor:
    def __init__(self):
        pass

    async def execute(self, function_object, function_input, all_states=None, stream=False):
        # 检查function_object是否是异步函数
        if asyncio.iscoroutinefunction(function_object):
            tool_result = await function_object(**function_input)
        else:
            tool_result = function_object(**function_input)
        result = {
            "execute_result":{
                "result":tool_result,
            },
            "all_states":all_states
        }
        return result