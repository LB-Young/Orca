import re
import json
# from Orca.executor.actions.llm_call import LLMCall


class CircularBlock():
    def __init__(self):
        pass

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

    async def analysis(self, content, all_states=None):
        # flag, type = self.validate(content)
        flag, type = True, "for"
        if not flag:
            raise ValueError
        if type == "for":
            iter_item, iter_list_values, for_content = await self.for_executor(content, all_states)
        elif type == "遍历":
            resp, all_states = await self.chinese_executor(content, all_states)
        result = {
            "result": "",
            "analysis_result":{
                "type": type,
                "iter_v":iter_item,
                "iter_list":iter_list_values,
                "for_content":for_content
            },
            "executed": False,
            "all_states":all_states
        }
        return result

    async def chinese_executor(self, content, all_states=None):
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

    async def for_executor(self, content, all_states=None):
        """
FOR $item in $for_value:
    根据$item写一个笑话 ->>result1
    @functions1(arg1=$item) ->>result2
END
        """
        print("待分析的for语句:", content)
        goto_content = "next"
        resp = []
        # 匹配FOR语句的外部语句和内部执行体
        # 外部语句格式: FOR $item in $list:
        # 内部执行体: 从冒号后到END之前的所有内容
        # content = content.strip()
        # if content[-3:] == "END":
        #     content = content[:-3].strip()
        get_for_pattern = r'(\s*FOR *\$[a-zA-Z0-9_]+? *in *\$[a-zA-Z0-9_]+ *[:：]?)(.*)\s*END\s*'
        for_block_res = re.match(get_for_pattern, content, re.DOTALL)
        if not for_block_res:
            raise ValueError("无效的FOR语句格式")
        # group(1)为外部语句
        for_language = for_block_res.group(1).strip()
        # group(2)为内部执行体
        for_content = for_block_res.group(2).strip()
        
        for_language_item_variable_pattern = re.compile(r'\$\w+')
        matches = for_language_item_variable_pattern.findall(for_language)

        if len(matches) == 2:
            iter_item = matches[0]
            iter_list_key = matches[1].strip()[1:]
            iter_list_values = all_states["variables_pool"].get_variables(iter_list_key)
            return iter_item, iter_list_values, for_content
        else:
            raise Exception("无效的FOR语句格式")

async def functions1(arg1):
    return "functions1:"+arg1

async def ut():
    import os
    import sys
    sys.path.append("F:\Cmodels\Orca\src")
    from Orca.vta.variables_pool import VariablesPool
    from Orca.vta.tools_agents_pool import ToolsAgentsPool
    from Orca.debug.debug_info import DebugInfo
    from Orca.config import Config
    for_prompt = """
FOR $item in $for_value:
    根据$item写一个笑话 ->>result1
    @functions1(arg1=$item) ->>result2
END
"""
    variables_pool = VariablesPool()
    tools_agents_pool = ToolsAgentsPool()
    debug_infos = DebugInfo()
    config = Config()
    variables_pool.add_variable("for_value", ["小明", "小红", "小刚"], "list")
    tools_agents_pool.add_tools({"functions1":functions1})
    all_states = {
                "variables_pool":variables_pool, 
                "tools_agents_pool":tools_agents_pool, 
                "debug_infos":debug_infos,
                "config":config, 
            }
    block = CircularBlock()
    res = await block.execute(for_prompt, all_states)
    print(res)

if __name__ == '__main__':
    import asyncio
    asyncio.run(ut())