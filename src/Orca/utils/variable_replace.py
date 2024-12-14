import re


async def replace_variable(prompt, all_states):
    
    prompt_variable_pattern = re.compile(r'\$[a-zA-Z0-9_]+')
    matches = prompt_variable_pattern.findall(prompt)
    replace_dict = {}
    for match in matches:
        variable_name = match[1:]
        value = all_states['variables_pool'].get_variables(variable_name)
        replace_dict[match] = value
    for key, value in replace_dict.items():
        if isinstance(value, str):
            prompt = prompt.replace(key, '"'+value+'"')
        else:
            prompt = prompt.replace(key, str(value))
    return prompt