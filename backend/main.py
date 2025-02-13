#!/usr/bin/env python
# -*- coding:utf-8 -*-
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import uuid
import os
import sys
abs_path = os.path.abspath(__file__)
cur_path = abs_path.split("backend")[0]
sys.path.append(rf"{cur_path}" + "src")
sys.path.append("/Users/liubaoyang/Documents/YoungL/Personal_project/tools_set")
import redis.asyncio as redis
from collections.abc import AsyncGenerator
from Orca import OrcaExecutor
from Orca import all_tools
from tools import other_tools
all_tools.update(other_tools)
import uvicorn
import asyncio

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis连接
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def load_api_key(platform):
    with open("/Users/liubaoyang/Documents/windows/api_key.json", "r", encoding="utf-8") as f:
        api_dict = json.load(f)
    # print(api_dict)
    return api_dict.get(platform, None)

# 配置模型参数
default_config = {
    "default_model_api_key": load_api_key("aliyun"),
    "default_model_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "default_llm_model_name": "deepseek-v3",
    "deepseek_chat_model_api_key": load_api_key("deepseek"),
    "deepseek_chat_model_base_url": "https://api.deepseek.com",
    "deepseek_chat_llm_model_name": "deepseek-chat",
    "deepseek_code_llm_model_name": "deepseek-coder",
    "groq_api_key": load_api_key("groq"),
    "groq_llm_model_name": "llama3-8b-8192",
    "together_api_key": load_api_key("together"),
    "together_llm_model_name": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
}

class Message(BaseModel):
    role: str
    message: str

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    config: Optional[dict] = None
    task_type: str
    conversation_id: int
    variables: Optional[Dict] = None

class ChatResponse(BaseModel):
    session_id: str
    message: str

@app.post("/chat/create")
async def create_chat_session():
    session_id = str(uuid.uuid4())
    await redis_client.hset(f"chat:{session_id}", "history", json.dumps([]))
    return {"session_id": session_id}

# 添加任务类型到提示词文件的映射
TASK_PROMPT_MAPPING = {
    "论文推荐": "examples/paper_recommend/paper_recommend.orca",
    "志愿专家团": "examples/multi_roles/multi_roles.orca",
    "其他任务": "examples/rag_agent/rag_agent.orca"  # 默认使用通用提示词
}

# 修改加载Orca提示词函数
def load_orca_prompt(task_type: str) -> tuple:
    """
    根据任务类型加载对应的Orca提示词
    参数:
        task_type: 任务类型，如"论文推荐"、"志愿专家团"等
    返回:
        content: 提示词内容
        variables: 提示词变量
    """
    # 获取对应的提示词文件路径
    prompt_file = TASK_PROMPT_MAPPING.get(task_type, TASK_PROMPT_MAPPING["其他任务"])
    orca_prompt_path = os.path.join(cur_path, prompt_file)
    
    try:
        with open(orca_prompt_path, "r", encoding="utf-8") as f:
            orca_file = f.read()
        content = orca_file.split("orca:", 1)[-1].strip()
        variables = json.loads(orca_file.split("orca:", 1)[0].strip().split("variabes:", 1)[-1].strip())
        return content, variables
    except FileNotFoundError:
        print(f"Warning: Prompt file for task type '{task_type}' not found, using default prompt.")
        # 如果找不到对应的提示词文件，使用默认提示词
        default_path = os.path.join(cur_path, TASK_PROMPT_MAPPING["其他任务"])
        with open(default_path, "r", encoding="utf-8") as f:
            orca_file = f.read()
        content = orca_file.split("orca:", 1)[-1].strip()
        variables = json.loads(orca_file.split("orca:", 1)[0].strip().split("variabes:", 1)[-1].strip())
        return content, variables

# 修复WebSocket处理函数中的错误
@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    try:
        # 接受WebSocket连接
        await websocket.accept()
        
        while True:
            try:
                # 接收消息
                data = await websocket.receive_json()
                request = ChatRequest(**data)
                
                # 处理新会话
                if not request.variables:
                    try:
                        orca_content, variables = load_orca_prompt(request.task_type)
                        variables["query"] = []
                    except Exception as e:
                        await websocket.send_json({
                            "error": f"加载提示词失败: {str(e)}",
                            "is_final": True
                        })
                        continue
                else:
                    variables = request.variables
                    orca_content = load_orca_prompt(request.task_type)[0]
                
                # 添加用户消息
                variables["query"].append({"role": "user", "content": request.message})
                
                # 初始化执行器
                init_params = {  # 修正拼写错误
                    "configs": load_config(),
                    "memories": [],
                    "debug_infos": [],
                    "variables": variables,
                    "tools": all_tools,
                    "default_agent": {
                        "flag": False,
                        "roles": {},
                        "tools": "default",
                        "agents": "default",
                    }
                }
                
                # 执行对话
                executor = OrcaExecutor()
                executor.init_executor(init_params=init_params)  # 修正参数名
                response = await executor.execute(prompt=orca_content, stream=True)
                
                # 流式返回响应
                full_response = ""
                async for res, execute_state in response:
                    if execute_state == "processed":
                        chunk = res['variables_pool'].get_variables('final_result')
                        full_response += chunk
                        print(chunk, end="")
                        await websocket.send_json({
                            "chunk": chunk,
                            "is_final": False,
                            "variables": variables
                        })
                
                # 发送最终响应
                variables["query"].append({"role": "assistant", "content": full_response})
                await websocket.send_json({
                    "chunk": "",
                    "is_final": True,
                    "variables": variables
                })
                
            except WebSocketDisconnect:
                # 客户端断开连接，退出循环
                print("Client disconnected")
                break
            except Exception as e:
                # 处理其他异常
                print(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "is_final": True
                })
                break
                
    except Exception as e:
        # 处理 WebSocket 连接异常
        print(f"WebSocket connection error: {str(e)}")
    finally:
        # 确保连接正确关闭
        try:
            await websocket.close()
        except:
            pass

# 加载配置文件
def load_config() -> Dict:
    """加载配置信息"""
    default_config = {
        "default_model_api_key": load_api_key("aliyun"),
        "default_model_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_llm_model_name": "deepseek-v3",
        "deepseek_chat_model_api_key": load_api_key("deepseek"),
        "deepseek_chat_model_base_url": "https://api.deepseek.com",
        "deepseek_chat_llm_model_name": "deepseek-chat",
        "deepseek_code_llm_model_name": "deepseek-coder",
        "groq_api_key": load_api_key("groq"),
        "groq_llm_model_name": "llama3-8b-8192",
        "together_api_key": load_api_key("together"),
        "together_llm_model_name": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    }
    return default_config

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)