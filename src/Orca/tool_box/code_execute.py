import json
import asyncio
from Orca.segment_executor.llm_client import LLMClient


async def create_function_from_string(function_string):
    """
    将字符串形式的函数代码转换为可调用的函数对象
    
    Args:
        function_string (str): 包含函数定义的字符串
        
    Returns:
        function: 可调用的函数对象
    """
    # 创建一个新的命名空间来存储函数
    namespace = {}
    
    # 在新的命名空间中执行函数定义
    exec(function_string, namespace)
    
    # 返回创建的函数对象
    function_name = function_string.split("(")[0].split("def ")[1].strip()

    return namespace[function_name]

async def code_execute(code="", code_params=None, all_states=None, params_format=False):
    if params_format:
        return ['code', 'code_params']
    try:
        return_index = code.rfind("return")
        split_index = code.find("\n", return_index) 
        new_code = code[:split_index]
        params_content = code[split_index:]
        my_func = await create_function_from_string(new_code)
        try:
            result = await my_func(**code_params)
        except:
            config_dict = all_states['config'].get_configs()
            llm_client = LLMClient(config_dict)
            return_foramt = '{"param1":"value1"}'
            prompt = f"""我想要调用一个函数，函数代码如下：\n{new_code}\n\n调用示例：\n{params_content}\n\n你需要从调用示例中提取出调用上方函数需要传递的参数，直接以{return_foramt}的形式返回，不要返回其它内容。"""
            result = await llm_client.generate_answer(prompt)
            if "```" in result:
                result = result.split("```json")[1].split("```")[0]
            extract_params = json.loads(result)
            if asyncio.iscoroutinefunction(my_func):
                result = await my_func(**extract_params)
            else:
                result = my_func(**extract_params)
        return str(result)
    except:
        raise Exception("代码执行器出错！")