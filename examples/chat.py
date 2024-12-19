#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2024/10/17    15:11
# @Author    :Young.lius
# tips       :
import os
import sys
abs_path = os.path.abspath(__file__)
cur_path = abs_path.split("examples")[0] + "\src"
sys.path.append(rf"{cur_path}")
sys.path.append(r"F:\Cmodels\Personal_project\tools_set")

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import json
from dotenv import load_dotenv
from Orca import OrcaExecutor
from Orca import all_tools
from tools import other_tools

orca_prompt_path = r"F:\Cmodels\Orca_branch\main\Orca\examples\paper_recommend\paper_recommend.orca"

orca_prompt_path = abs_path[:abs_path.index("example")] + orca_prompt_path[orca_prompt_path.index("examples"):]

def load_api_key(platform):
    with open(r"C:\Users\86187\Desktop\api_key.json", "r", encoding="utf-8") as f:
        api_dict = json.load(f)
    # print(api_dict)
    return api_dict.get(platform, None)

load_dotenv()
default_api_key = load_api_key("deepseek")
default_base_url = "https://api.deepseek.com"
default_llm_model_name = "deepseek-chat"
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

with open(orca_prompt_path, "r", encoding="utf-8") as f:
    orca_file = f.read()

all_tools.update(other_tools)

content = orca_file.split("orca:", 1)[-1].strip()
variables = json.loads(orca_file.split("orca:", 1)[0].strip().split("variabes:", 1)[-1].strip())

if "false" in orca_file.split("orca:", 1)[0].split("variabes:", 1)[0] or "False" in orca_file.split("orca:", 1)[0].split("variabes:", 1)[0]:
    agent_flag = False
else:
    agent_flag = True
variables["query"] = []

async def main():
    query = input('请输入问题：')
    while len(query) != 0:
        variables["query"].append({"role":"user", "message":query})
        init_params = {
            "configs": config,
            "memories": [],
            "debug_infos": [],
            "variables": variables,
            "tools": all_tools,
            "default_agent":{
                "flag":agent_flag,
                "roles": {},
                "tools":"default",
                "agents":"default",
                    }
                }
        
        executor = OrcaExecutor()
        executor.init_executor(init_parmas=init_params)
        res, execute_state  = await executor.execute(prompt=content)
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
            res, execute_state = await executor.execute(content, breakpoint_infos=new_init_params, mode=mode)

        logger.info(res['variables_pool'].get_variables('final_result'))
        logger.info("--"*50)
        variables["query"].append({"role":"assistant", "message":res['variables_pool'].get_variables('final_result')})
        query = input('请输入问题：')
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())