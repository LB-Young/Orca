async def dict_to_multiline_string(dict_data, indent=0, params_format=False):

    if params_format:
        return ['dict_data', 'indent']
    result = ""
    for key, value in dict_data.items():
        if isinstance(value, dict):  # 如果值是字典，递归处理
            inner = await dict_to_multiline_string(value, indent + 4)
            result += " " * indent + f"{key}:\n" + inner
        else:  # 否则直接添加键值对
            result += " " * indent + f"{key}: {value}\n"
    return result