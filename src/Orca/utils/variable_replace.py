import re
import logging

logger = logging.getLogger(__name__)

async def replace_variable(prompt, all_states):
    prompt_variable_pattern = re.compile(r'\$[a-zA-Z_][a-zA-Z0-9_]*(?:(?:\.[a-zA-Z_][a-zA-Z0-9_]*)|(?:\[\d+\]))*')
    # prompt_variable_pattern = re.compile(r'\$[a-zA-Z0-9_]+')
    matches = prompt_variable_pattern.findall(prompt)
    logger.debug(matches)
    replace_dict = {}
    for match in matches:
        variable_name = match[1:]
        if "." not in match and "[" not in match:
            value = all_states['variables_pool'].get_variables(variable_name)
            replace_dict[match] = value
        else:
            while "[0" in variable_name and "[0]" not in variable_name:
                variable_name = variable_name.replace("[0", "[")

            variable_first_name  = variable_name.split('.')[0].strip().split('[')[0].strip()
            variable_value = all_states['variables_pool'].get_variables(variable_first_name)
            varuable_full_index = variable_name.replace(variable_first_name, str(variable_value))
            value = eval(varuable_full_index)
            replace_dict[match] = value
            
    for key, value in replace_dict.items():
        if isinstance(value, str):
            prompt = prompt.replace(key, '"'+value+'"')
        else:
            prompt = prompt.replace(key, str(value))
    return prompt
