import re

async def parse_string_to_dict(input_str):
    """
    Parse a string of key-value pairs into a dictionary using regex.
    """
    # 去掉首尾的大括号
    s = input_str.strip()
    if not (s.startswith('{') and s.endswith('}')):
        return {}
    s = s[1:-1].strip()
    
    # 用正则表达式分割键值对
    # 匹配模式：在引号后面跟着可选的空白字符和逗号，然后是新的键
    parts = re.split(r'(?:\s*,\s*"(?=[a-zA-Z0-9_]))', s)
    result = {}
    for part in parts:
        # 确保每部分都是一个有效的键值对
        key, value = part.split('=', 1)
        if key.strip()[0] == '"':
            key = key.strip()[1:]
        if key.strip()[-1] == '"':
            key = key.strip()[:-1]
        if value.strip()[0] == '"':
            value = value.strip()[1:]
        if value.strip()[-1] == '"':
            value = value.strip()[:-1]
        result[key] = value
        
    return result