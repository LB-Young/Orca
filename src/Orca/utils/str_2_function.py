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