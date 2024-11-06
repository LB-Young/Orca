#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2024/10/17    15:11
# @Author    :Young.liu
# tips       :
import os
from dotenv import load_dotenv
from Orca.Orca import OrcaExecutor
from api import set_api_key
set_api_key()
load_dotenv()
default_api_key = os.environ.get("DEFAULT_MODEL_API_KEY")
default_base_url = os.getenv("DEFAULT_MODEL_BASE_URL")
default_llm_model_name = os.getenv("DEFAULT_LLM_MODEL_NAME")
deepseek_api_key = os.environ.get("DEEPSEEK_CHAT_MODEL_API_KEY")
deepseek_model_base_url = os.getenv("DEEPSEEK_CHAT_MODEL_BASE_URL")
deepseek_llm_model_name = os.getenv("DEEPSEEK_CHAT_LLM_MODEL_NAME")

groq_api_key = os.environ.get("Groq_API_KEY")
groq_llm_model_name = os.getenv("Groq_LLM_MODEL_NAME")

together_api_key = os.environ.get("Together_API_KEY")
together_llm_model_name = os.getenv("Together_LLM_MODEL_NAME")
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
orca_prompt_path = r"F:\Cmodels\GIT_Orca\Orca\examples\agent_prompt.orca"
with open(orca_prompt_path, "r", encoding="utf-8") as f:
    content = f.read()

variables = {
    "query": "AI 撰写"
}
tool = {
    "web_search": "websearch",
}

init_params = {
    "config": config,
    "memories": [],
    "debug_infos": [],
    "variables": variables,
    "tools": tool,
}
async def main():
    executor = OrcaExecutor()
    executor.init_executor(init_parmas=init_params)
    res = await executor.execute(prompt=content)
    print(res.keys())
    while "breakpoint_infos" in res.keys():
        mode = input("请输入运行模式：")
        executor.init_executor(init_parmas=res['breakpoint_infos'])
        res = await executor.execute(content, breakpoint_infos=res["breakpoint_infos"], mode=mode)
    print(res)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
