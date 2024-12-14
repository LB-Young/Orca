import io
import sys



async def code_execute(code="", code_params=None, params_format=False):
    if params_format:
        return ['code', 'code_params']
    try:
        my_func = eval(code)
        result = my_func(**code_params)
        return result
    except:
        raise Exception("代码执行器出错！")