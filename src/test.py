import re

def parse_string_to_dict(input_str):
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
    parts = re.split(r'"(?:\s*,\s*"(?=[a-zA-Z0-9_]))', s)
    result = {}
    for part in parts:
        # 确保每部分都是一个有效的键值对
        key, value = part.split('=', 1)
        result[key] = value
        
    return result

# 测试代码
test_input = """{"content"="主人，早上好！\n我为您收集了最"新的论"文，并根据您的研究方向给"出以下阅读建议"：\n\n-----------------------------------------------------------------------------------------------------------------------------\n$recommend", "subject"="daily paper recommend", "to"="lby15356@gmail.com"}"""

result = parse_string_to_dict(test_input)
print("解析结果：")
for k, v in result.items():
    print(f"{k}: {v}")
