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
    parts = re.split(r'"(?:\s*,\s*"(?=[a-zA-Z0-9_]))', s)
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


async def ut():
    result = await parse_string_to_dict("""{"content"=""当然，我很乐意为你写一首诗！以下是一首简短的诗：\n\n---\n\n**《晨曦》**\n\n晨曦微露，  \n轻纱笼罩大地，  \n鸟儿唤醒沉睡的梦，  \n阳光洒满心田。\n\n微风拂过
，  \n带来远方的气息，  \n树叶沙沙作响，  \n仿佛诉说着昨日的故事。\n\n我站在这片宁静中，  \n感受生命的脉动，  \n愿每一个清晨，  \n都如这般美好。\n\n---\n\n希望你喜欢这首 
诗！如果你有任何特定的主题或情感想要表达，也可以告诉我，我可以根据你的需求创作。"", "path"=""F:/logs/orca/output/casual/result.txt""}""")
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(ut())