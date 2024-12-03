#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2024/10/17    15:11
# @Author    :Young.liu
# tips       :
import os
import sys
import json
sys.path.append(r"F:\Cmodels\Orca\src")
from dotenv import load_dotenv
from Orca import OrcaExecutor
from Orca import all_tools
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
    "groq_api_key": groq_api_key,
    "groq_llm_model_name": groq_llm_model_name,
    "together_api_key": together_api_key,
    "together_llm_model_name": together_llm_model_name
}

orca_prompt_path = r"F:\Cmodels\Orca\examples\0.1.2\if.orca"
with open(orca_prompt_path, "r", encoding="utf-8") as f:
    content = f.read()


init_params = {
    "config": config,
    "memories": [],
    "debug_infos": [],
    "variables": {"input": "1"},
    "tools": all_tools,
    "default_agent":False}
async def main():
    executor = OrcaExecutor()
    executor.init_executor(init_parmas=init_params)
    res = await executor.execute(prompt=content)
    print(res.keys())
    while "breakpoint_infos" in res.keys():
        mode = input("请输入运行模式：")
        executor.init_executor(init_parmas=res['breakpoint_infos'])
        res = await executor.execute(content, breakpoint_infos=res["breakpoint_infos"], mode=mode)
    print("--"*50)
    print(res['variables_pool'].get_variables())
    print("--"*50)
    print(res['variables_pool'].get_variables('result'))
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
