import asyncio
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)

class ToolCallExecutor:
    def __init__(self):
        pass

    async def execute(self, function_object, function_input, all_states=None, stream=False):
        """
        执行工具函数调用
        
        Args:
            function_object: 要执行的工具对象
            function_input: 函数的输入参数
            all_states: 包含执行状态的字典
            stream: 是否使用流式输出
            
        Returns:
            包含执行结果和状态的字典
        """
        logger.debug(f"执行工具: {function_object.__class__.__name__ if hasattr(function_object, '__class__') else str(function_object)}")
        logger.debug(f"工具参数: {function_input}")
        
        # 处理特殊工具参数
        if 'BrowserUseTool' in str(function_object) or "CodeExecuteTool" in str(function_object):
            function_input['all_states'] = all_states
        
        # 定义空的属性字典
        properties = {}
        
        try:
            # 使用工具对象的arun方法
            logger.debug("开始执行工具函数的arun方法")
            tool_result = await function_object.arun(inputs=function_input, properties=properties)
            logger.debug(f"工具执行完成: {type(tool_result)}")
            
            # 处理执行结果
            result = {
                "execute_result": {
                    "result": tool_result,
                    "success": True
                },
                "all_states": all_states
            }
            
            logger.debug("工具执行成功完成")
            return result
            
        except Exception as e:
            logger.error(f"工具执行失败: {str(e)}")
            raise e  # 保持与原实现一致，继续抛出异常