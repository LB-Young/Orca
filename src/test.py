def create_function_from_string(function_string):
    """
    使用 eval 将字符串形式的函数代码转换为可调用的函数对象
    
    Args:
        function_string (str): 包含函数定义的字符串
        
    Returns:
        function: 可调用的函数对象
    """
    return eval(f"lambda a: {function_string}")

# 示例使用
function_body = '''
"化学" if "化学" in a else "物理"
'''

get_topic = create_function_from_string(function_body.strip())