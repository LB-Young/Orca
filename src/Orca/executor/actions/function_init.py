import re
import json


class FunctionInit:
    def __init__(self):
        pass

    async def analysis(self, prompt_content, all_states=None):
        analysis = await self.prompt_info_extract(prompt_content, all_states)
        tool = {
            analysis['function_name']: {
                                "object":analysis['object'],
                                'type': analysis['type'],
                                "describe":analysis['describe'],
                            }    
        }
        result = {
            "result":"",
            "analysis_result":tool,
            "executed":False,
            "all_states":all_states
        }
        return result

    async def prompt_info_extract(self, prompt_content, all_states=None):
        cur_prompt = prompt_content.replace("```", "").strip()
        if cur_prompt.startswith("workflow"):
            type = "workflow_init"
            cur_prompt = cur_prompt.replace("workflow", "").strip()
        elif cur_prompt.startswith("python"):
            type = "python_init"
            cur_prompt = cur_prompt.replace("python", "").strip()
        else:
            raise Exception(f"Prompt content type not supported:{prompt_content}")
        if "def" not in cur_prompt:
            raise Exception(f"Prompt content error{prompt_content}")
        elif cur_prompt.count("def") > 1:
            raise Exception(f"Prompt contain >=2 def keyword,{prompt_content}")
        else:
            describe_content_list = cur_prompt.split("def")
            describe = describe_content_list[0].strip()
            function_obj = "def" + describe_content_list[1]
            function_name = describe_content_list[1].split("(")[0].split("（")[0].split(":")[0].split("：")[0].strip()
        info = {
            "type":type,
            "function_name":function_name,
            "describe":describe,
            "object":function_obj
        }
        return info
