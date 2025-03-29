import os
import json
from typing import Optional, Dict, List, Union, AsyncGenerator
from abc import ABC, abstractmethod
import openai
from openai import AsyncOpenAI
import anthropic
import together
from groq import Groq
import logging

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """LLM客户端基类，定义通用接口"""
    
    @abstractmethod
    async def generate_completion(self, 
                                messages: List[Dict[str, str]], 
                                model: str,
                                stream: bool = False,
                                tools: Optional[List[Dict]] = None,
                                **kwargs) -> AsyncGenerator[str, None]:
        """生成补全响应"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    async def generate_completion(self, 
                                messages: List[Dict[str, str]], 
                                model: str,
                                stream: bool = False,
                                tools: Optional[List[Dict]] = None,
                                **kwargs) -> AsyncGenerator[str, None]:
        try:
            # 准备请求参数
            params = {
                "model": model,
                "messages": messages,
                "stream": stream,
                **kwargs
            }
            
            # 如果提供了tools，添加到参数中
            if tools:
                params["tools"] = tools
            
            # 调用API
            response = await self.client.chat.completions.create(**params)
            
            if stream:
                async for chunk in response:
                    # print(chunk)
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                if tools and response.choices[0].message.tool_calls:
                    # 如果是工具调用，返回特定格式
                    tool_call = response.choices[0].message.tool_calls[0]
                    yield f"{tool_call.function.name}:{tool_call.function.arguments}"
                else:
                    # 普通响应
                    yield response.choices[0].message.content
                    
        except Exception as e:
            yield f"Error with OpenAI API: {str(e)}"


class AnthropicClient(BaseLLMClient):
    """Anthropic API客户端"""
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_completion(self, 
                                messages: List[Dict[str, str]], 
                                model: str,
                                stream: bool = False,
                                tools: Optional[List[Dict]] = None,
                                **kwargs) -> AsyncGenerator[str, None]:
        try:
            # 转换消息格式为Anthropic格式
            prompt = self._convert_messages_to_prompt(messages)
            
            response = await self.client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=stream,
                **kwargs
            )
            
            if stream:
                async for chunk in response:
                    if chunk.content:
                        yield chunk.content[0].text
            else:
                yield response.content[0].text
                
        except Exception as e:
            yield f"Error with Anthropic API: {str(e)}"
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将OpenAI格式的消息转换为Anthropic格式"""
        converted = []
        for msg in messages:
            role = "Human" if msg["role"] == "user" else "Assistant"
            converted.append(f"{role}: {msg['content']}")
        return "\n".join(converted)


class TogetherClient(BaseLLMClient):
    """Together API客户端"""
    def __init__(self, api_key: str):
        self.client = together.Together(api_key)
    
    async def generate_completion(self, 
                                messages: List[Dict[str, str]], 
                                model: str,
                                stream: bool = False,
                                tools: Optional[List[Dict]] = None,
                                **kwargs) -> AsyncGenerator[str, None]:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                **kwargs
            )
            
            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content
                
        except Exception as e:
            yield f"Error with Together API: {str(e)}"


class GroqClient(BaseLLMClient):
    """Groq API客户端"""
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    async def generate_completion(self, 
                                messages: List[Dict[str, str]], 
                                model: str,
                                stream: bool = False,
                                tools: Optional[List[Dict]] = None,
                                **kwargs) -> AsyncGenerator[str, None]:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                **kwargs
            )
            
            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content
                
        except Exception as e:
            yield f"Error with Groq API: {str(e)}"


class LLMClient:
    """统一的LLM客户端接口"""
    def __init__(self, config_dict: Dict):
        self.config = config_dict
        self.clients = {}
        self._initialize_clients()
        
    def _initialize_clients(self):
        """初始化各平台的客户端"""
        # OpenAI
        if "openai" in self.config:
            self.clients["openai"] = OpenAIClient(
                api_key=self.config["openai"]["api_key"],
                base_url=self.config["openai"].get("base_url")
            )
            self.model = self.config['openai']['model'] 
            
        # Anthropic
        if "anthropic" in self.config:
            self.clients["anthropic"] = AnthropicClient(
                api_key=self.config["anthropic"]["api_key"]
            )
            self.model = self.config['anthropic']['model']
            
        # Together
        if "together" in self.config:
            self.clients["together"] = TogetherClient(
                api_key=self.config["together"]["api_key"]
            )
            self.model = self.config['together']['model']
        # Groq
        if "groq" in self.config:
            self.clients["groq"] = GroqClient(
                api_key=self.config["groq"]["api_key"]
            )
            self.model = self.config['groq']['model']

    def _get_platform_from_model(self, model: str) -> str:
        """根据模型名称判断平台"""
        model = model.lower()
        if any(x in model for x in ["gpt", "azure"]):
            return "openai"
        elif "claude" in model:
            return "anthropic"
        elif "groq" in model:
            return "groq"
        elif any(x in model for x in ["llama", "mistral", "mixtral"]):
            return "together"
        else:
            return "openai"  # 默认使用OpenAI
    
    async def generate_answer(self, 
                            messages: Optional[List[Dict[str, str]]] = None,
                            prompt: Optional[str] = None,
                            model: Optional[str] = None,
                            stream: bool = False,
                            tools: Optional[List[Dict]] = None,
                            mode: str = "chat",  # 新增 mode 参数，可选值：chat/code/function
                            **kwargs) -> AsyncGenerator[str, None]:
        """统一的生成接口
        
        Args:
            messages: 消息历史
            prompt: 单条提示语
            model: 模型名称
            stream: 是否使用流式输出
            tools: 可用的工具列表
            mode: 生成模式，可选值：
                - chat: 普通对话模式
                - code: 代码生成模式
                - function: 函数选择模式
            **kwargs: 其他参数
        """
        # 处理输入
        if prompt and not messages:
            messages = [{"role": "user", "content": prompt}]
            
        # 根据不同模式添加系统提示
        if mode == "code":
            system_message = {
                "role": "system",
                "content": "You are a helpful coding assistant. Please provide clear, well-commented code."
            }
            messages = [system_message] + (messages or [])
        elif mode == "function":
            if not tools:
                yield "Error: Tools must be provided in function mode"
                return
            system_message = {
                "role": "system",
                "content": "You are a helpful assistant that chooses the appropriate function to call."
            }
            messages = [system_message] + (messages or [])
            stream = False  # 函数选择模式强制使用非流式
            
        # 获取模型名称
        model = self.model
            
        # 获取对应的平台
        platform = self._get_platform_from_model(model)
        
        if platform not in self.clients:
            yield f"Error: Platform {platform} not configured"
            return
            
        # 调用对应平台的客户端
        client = self.clients[platform]
        
        # 收集完整响应（用于函数调用模式）
        complete_response = ""
        # print("messages:", messages)
        async for response in client.generate_completion(
            messages=messages,
            model=model,
            stream=stream,
            tools=tools,
            **kwargs
        ):  
            # print("response:", list(response))
            if mode == "function":
                complete_response += response
            else:
                yield response
                
        # 如果是函数调用模式，解析并返回结果
        if mode == "function" and complete_response:
            if ":" in complete_response:
                function_name, function_params = complete_response.split(":", 1)
                yield f"{function_name}:{function_params}"
            else:
                yield complete_response
