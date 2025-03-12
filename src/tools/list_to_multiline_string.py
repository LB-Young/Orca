from .dict_to_multiline_string import dict_to_multiline_string


async def list_to_multiline_string(list_data=[], params_format=False):
  if params_format:
    return ['list_data']
  result = ""
  for item in list_data:
    if isinstance(item, list):
      result += await list_to_multiline_string(item) + "\n"
    elif isinstance(item, dict):
      result += await dict_to_multiline_string(item, 0) + "\n"
    else:
      result += str(item) + "\n"
  return result