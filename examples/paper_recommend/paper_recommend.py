#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2024/10/17    15:11
# @Author    :Young.liu
# tips       :
import os
import sys
import json
sys.path.append("/Users/liubaoyang/Documents/YoungL/project/Orca/src")
sys.path.append("/Users/liubaoyang/Documents/YoungL/project/Personal_project/tools_set")
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from Orca import OrcaExecutor
from Orca import all_tools
def load_api_key(platform):
    with open("/Users/liubaoyang/Documents/windows/api_key.json", "r", encoding="utf-8") as f:
        api_dict = json.load(f)
    # print(api_dict)
    return api_dict.get(platform, None)

load_dotenv()
default_api_key = load_api_key("aliyun")
default_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
default_llm_model_name = "qwen-max-latest"
deepseek_api_key = load_api_key("deepseek")
deepseek_model_base_url = "https://api.deepseek.com"
deepseek_llm_model_name = "deepseek-chat"
deepseek_code_llm_model_name = "deepseek-coder"
groq_api_key = load_api_key("groq")
groq_llm_model_name = "llama3-8b-8192"

together_api_key = load_api_key("together")
together_llm_model_name = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
config = {
    "default_model_api_key": default_api_key,
    "default_model_base_url": default_base_url,
    "default_llm_model_name": default_llm_model_name,
    "deepseek_chat_model_api_key": deepseek_api_key,
    "deepseek_chat_model_base_url": deepseek_model_base_url,
    "deepseek_chat_llm_model_name": deepseek_llm_model_name,
    "deepseek_code_llm_model_name": deepseek_code_llm_model_name,
    "groq_api_key": groq_api_key,
    "groq_llm_model_name": groq_llm_model_name,
    "together_api_key": together_api_key,
    "together_llm_model_name": together_llm_model_name
}

orca_prompt_path = "/Users/liubaoyang/Documents/YoungL/project/Orca/examples/paper_recommend/paper_recommend_new_full.orca"  # 输入workflow prompt路径
with open(orca_prompt_path, "r", encoding="utf-8") as f:
    orca_file = f.read()


content = orca_file.split("orca:", 1)[-1].strip()
variables = json.loads(orca_file.split("orca:", 1)[0].strip().split("variabes:", 1)[-1].strip())

if "false" in orca_file.split("orca:", 1)[0].split("variabes:", 1)[0] or "False" in orca_file.split("orca:", 1)[0].split("variabes:", 1)[0]:
    agent_flag = False
else:
    agent_flag = True

from tools import other_tools
all_tools.update(other_tools)

init_params = {
    "configs": config,
    
    "memories": [],
    "debug_infos": [],
    "variables": variables,
    "tools": all_tools,
    "default_agent":{
        "flag":agent_flag,
        "roles": {
            "finance_expert": "金融专家",
            "law_expert": "法律专家",
            "medical_expert": "医疗专家",
            "computer_expert": "计算机专家",
                }
            }
        }
async def main():
    executor = OrcaExecutor()
    executor.init_executor(init_params=init_params)
    response = await executor.execute(prompt=content, stream=True)
    async for res, execute_state in response:
        # print(res['variables_pool'].get_variables('final_result'))
        if execute_state == "processed":
            print(res['variables_pool'].get_variables('final_result'), end="", flush=True)
        else:
            pass

    while execute_state == "bp":
        mode = input("请输入运行模式：")
        new_init_params = {
            "configs": res['config'].get_configs(),
            "memories": [],
            "debug_infos": res['debug_infos'].get_debug_infos(),
            "variables": res['variables_pool'].get_variables(),
            "tools": res['tools_agents_pool'].get_tools(),
            "agents": res['tools_agents_pool'].get_agents(),
            "prompt_segments": res['prompt_segments'],
        }
        executor.init_executor(init_parmas=new_init_params)
        res, execute_state = await executor.execute(content, breakpoint_infos=new_init_params, mode=mode, stream=True)
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
