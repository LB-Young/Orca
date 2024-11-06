import re
import json
from Orca.executor.actions.llm_call import LLMCall


class CircularBlock():
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variable_tool_pool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        self.llm_call = LLMCall(variable_tool_pool=self.variable_tool_pool, config=self.config, memories=self.memories, debug_infos=self.debug_infos)

    def validate(self, content):
        if content.strip().startswith("for"):
            if "{" in content:
                start_index = content.find("{")
            else:
                return False
            count_variable = 0
            s = []
            for item in content[start_index:]:
                if item == "{":
                    s.append("{")
                elif item == "}":
                    if len(s) == 0:
                        return False
                    else:
                        s.pop()
                        if len(s) == 0:
                            count_variable += 1
                else:
                    pass
            if count_variable >= 3:
                return True, "for"
            else:
                return False, "for"
        elif content.strip().startswith("遍历"):
            if "{" in content:
                start_index = content.find("{")
            else:
                return False
            count_variable = 0
            s = []
            for item in content[start_index:]:
                if item == "{":
                    s.append("{")
                elif item == "}":
                    if len(s) == 0:
                        return False
                    else:
                        s.pop()
                        if len(s) == 0:
                            count_variable += 1
                else:
                    pass
            if count_variable >= 1:
                return True, "遍历"
            else:
                return False, "遍历"

    async def execute(self, content):
        resp = []
        goto_content = None
        flag, type = self.validate(content)
        if not flag:
            raise ValueError
        if type == "for":
            resp, goto_content = await self.for_executor(content)
        elif type == "遍历":
            resp, goto_content = await self.chinese_executor(content)

        return resp, goto_content



    async def chinese_executor(self, content):
        goto_content = "next"
        resp = []
        get_for_pattern = r'( *遍历 *\{.*?\}.*? *:)(.*)'
        for_block_res = re.match(get_for_pattern, content, re.DOTALL)
        for_language = for_block_res.group(1)
        for_content = for_block_res.group(2)
        if "goto" in for_content:
            goto_content = for_content.split("goto")[-1].strip
        for_language_item_variable_pattern = re.compile(r'\{.*?\}')
        matches = for_language_item_variable_pattern.findall(for_language)
        if len(matches) == 1:
            iter_list_key = matches[0].strip()[1:-1]
            if iter_list_key.isdigit():
                return_iter_list = self.memories.get_memory(iter_list_key)[0]
                return_iter_list = return_iter_list['output']
                variable_need_index_content = for_language.split(iter_list_key)[-1]
                if variable_need_index_content[1] == ".":
                    key_list = variable_need_index_content[2:].strip()[:-1].strip().split(".")
                    cur_list = return_iter_list
                    for key in key_list:
                        if isinstance(cur_list, dict):
                            if key in cur_list.keys():
                                cur_list = cur_list[key]
                            else:
                                cur_list = []
                                break
                        else:
                            if len(key.strip())>0:
                                raise ValueError
                            else:
                                if isinstance(cur_list, list):
                                    pass
                                else:
                                    cur_list = []
                                    break
                    return_iter_list = cur_list
                if return_iter_list:
                    iter_list = return_iter_list
                    try:
                        iter_list = json.loads(iter_list)
                    except Exception as e:
                        iter_list = iter_list
                else:
                    iter_list = []
            else:
                if "[" not in iter_list_key:
                    iter_list = self.variable_tool_pool.get_variables(iter_list_key)
                else:
                    iter_list_str = iter_list_key.strip()[2:-2]
                    for_langueage_list_split_pattern = re.compile(r'[\'\"][,，] *[\'\"]')
                    iter_list = for_langueage_list_split_pattern.split(iter_list_str)

            if isinstance(iter_list, list):
                for item in iter_list:
                    prompt = f"待处理内容为：“{item}”。\n" + for_content
                    res = await self.llm_call.execute(content=prompt)
                    resp.append(res[0])
            else:
                pass
        else:
            pass
        return resp, goto_content

    async def for_executor(self, content):
        goto_content = "next"
        resp = []
        get_for_pattern = r'( *for *each *\{.*?\} *in *\{.*?\}.*? *:)(.*)'
        for_block_res = re.match(get_for_pattern, content, re.DOTALL)
        for_language = for_block_res.group(1)
        for_content = for_block_res.group(2)

        if "goto" in for_content:
            goto_content = for_content.split("goto")[-1].strip
        for_language_item_variable_pattern = re.compile(r'\{.*?\}')
        matches = for_language_item_variable_pattern.findall(for_language)
        if len(matches) == 2:
            iter_item = matches[0]
            iter_list_key = matches[1].strip()[1:-1]
            if iter_list_key.isdigit():
                return_iter_list = self.memories.get_memory(iter_list_key)[0]
                return_iter_list = return_iter_list['output']
                variable_need_index_content = for_language.split(iter_list_key)[-1]
                if variable_need_index_content[1] == ".":
                    key_list = variable_need_index_content[2:].strip()[:-1].strip().split(".")
                    cur_list = return_iter_list
                    for key in key_list:
                        if isinstance(cur_list, dict):
                            if key in cur_list.keys():
                                cur_list = cur_list[key]
                            else:
                                cur_list = []
                                break
                        else:
                            if len(key.strip())>0:
                                raise ValueError
                            else:
                                if isinstance(cur_list, list):
                                    pass
                                else:
                                    cur_list = []
                                    break
                    return_iter_list = cur_list
                if return_iter_list:
                    iter_list = return_iter_list
                    try:
                        iter_list = json.loads(iter_list)
                    except Exception as e:
                        iter_list = iter_list
                else:
                    iter_list = []
            else:
                if "[" not in iter_list_key:
                    iter_list = self.variable_tool_pool.get_variables(iter_list_key)
                else:
                    iter_list_str = iter_list_key.strip()[2:-2]
                    for_langueage_list_split_pattern = re.compile(r'[\'\"][,，] *[\'\"]')
                    iter_list = for_langueage_list_split_pattern.split(iter_list_str)

            if isinstance(iter_list, list):
                for item in iter_list:
                    item_value = "“"+str(item)+"”"
                    prompt = for_content.replace(iter_item, item_value)
                    res = await self.llm_call.execute(content=prompt)
                    resp.append(res[0])
            else:
                pass
        else:
            pass
        return resp, goto_content