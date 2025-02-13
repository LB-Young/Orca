# 导入必要的库
import streamlit as st  # 导入streamlit用于构建Web界面
import sys  # 导入sys用于修改系统路径
import os  # 导入os用于处理文件路径
import json  # 导入json用于处理JSON数据
import asyncio  # 导入asyncio用于异步操作
import websockets  # 导入websockets用于WebSocket通信
from typing import Dict, List, AsyncGenerator

# 添加项目根目录到系统路径
abs_path = os.path.abspath(__file__)
root_path = abs_path.split("frontend")[0]
sys.path.append(root_path)

# 导入聊天相关的模块
from examples.chat import OrcaExecutor, all_tools, other_tools, load_api_key

# 配置页面
st.set_page_config(
    page_title="AI助手",  # 设置页面标题
    layout="wide",  # 设置页面布局为宽屏
    initial_sidebar_state="expanded"  # 设置侧边栏初始状态为展开
)

# 初始化会话状态
if "messages" not in st.session_state:  # 初始化消息历史
    st.session_state.messages = []
if "task_type" not in st.session_state:  # 初始化任务类型
    st.session_state.task_type = "论文推荐"
if "conversation_id" not in st.session_state:  # 初始化会话ID
    st.session_state.conversation_id = 0
if "variables" not in st.session_state:
    st.session_state.variables = None

# WebSocket URL
WEBSOCKET_URL = "ws://localhost:8000/chat"

# 加载配置文件
def load_config() -> Dict:
    """
    加载配置信息
    返回: 配置字典
    """
    default_api_key = load_api_key("deepseek")
    config = {
        "default_model_api_key": default_api_key,
        "default_model_base_url": "https://api.deepseek.com",
        "default_llm_model_name": "deepseek-chat",
        # ... 其他配置项保持不变 ...
    }
    return config

# 加载Orca提示词
def load_orca_prompt() -> tuple:
    """
    加载Orca提示词
    返回: 内容和变量的元组
    """
    orca_prompt_path = os.path.join(root_path, "examples/rag_agent/rag_agent.orca")
    with open(orca_prompt_path, "r", encoding="utf-8") as f:
        orca_file = f.read()
    content = orca_file.split("orca:", 1)[-1].strip()
    variables = json.loads(orca_file.split("orca:", 1)[0].strip().split("variabes:", 1)[-1].strip())
    return content, variables

# 修改创建聊天界面函数
def create_chat_interface():
    """
    创建聊天界面的主要布局
    """
    # 创建左侧任务选择栏和新会话按钮
    with st.sidebar:
        # 添加新会话按钮
        if st.button("新会话", key="new_chat", use_container_width=True):
            start_new_conversation()
            st.rerun()
        
        # 任务类型选择框
        previous_task_type = st.session_state.task_type
        current_task_type = st.selectbox(
            "选择任务类型",
            ["论文推荐", "志愿专家团", "其他任务"]
        )
        
        # 如果任务类型改变，开启新会话
        if current_task_type != previous_task_type:
            st.session_state.task_type = current_task_type
            # 清空自定义变量
            st.session_state.custom_variables = "{}"
            st.session_state.variables = None
            start_new_conversation()
            st.rerun()
        
        # 添加JSON输入框
        st.markdown("### 参数设置")
        if "custom_variables" not in st.session_state:
            st.session_state.custom_variables = "{}"
            
        custom_variables = st.text_area(
            "Variables (JSON格式)",
            value=st.session_state.custom_variables,
            height=200,
            key="variables_input"
        )
        
        # 添加应用按钮
        if st.button("应用参数", use_container_width=True):
            try:
                # 验证JSON格式
                variables = json.loads(custom_variables)
                st.session_state.custom_variables = custom_variables
                st.session_state.variables = variables
                st.success("参数已更新")
                # 开始新会话
                start_new_conversation()
                st.rerun()
            except json.JSONDecodeError:
                st.error("无效的JSON格式")
    
    # 创建主聊天区域
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.title("AI助手")
        st.caption(f"会话 #{st.session_state.conversation_id}")
        
        # 显示当前参数
        with st.expander("当前参数"):
            st.json(st.session_state.variables if st.session_state.variables else {})
        
        # 显示聊天历史
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# 修改开始新会话函数
def start_new_conversation():
    """
    开始新的会话：清空消息历史并增加会话ID
    """
    st.session_state.messages = []  # 清空消息历史
    st.session_state.conversation_id += 1  # 增加会话ID
    # 不再重置variables，而是使用用户设置的值
    if not st.session_state.variables:
        try:
            st.session_state.variables = json.loads(st.session_state.custom_variables)
        except json.JSONDecodeError:
            st.session_state.variables = {}

# 修改错误处理装饰器
def handle_connection_error(func):
    """处理WebSocket连接错误的装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            async for item in func(*args, **kwargs):
                yield item
        except websockets.exceptions.ConnectionClosed:
            st.error("与服务器的连接已断开，请刷新页面重试")
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
    return wrapper

# 修改WebSocket通信函数
@handle_connection_error
async def chat_with_backend(message: str) -> AsyncGenerator[str, None]:
    """
    与后端服务通信
    Args:
        message: 用户输入的消息
    Yields:
        str: 服务器返回的响应块
    """
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            # 准备请求数据
            request_data = {
                "message": message,
                "task_type": st.session_state.task_type,
                "conversation_id": st.session_state.conversation_id,
                "variables": st.session_state.variables or json.loads(st.session_state.custom_variables)
            }
            
            # 发送请求
            try:
                await websocket.send(json.dumps(request_data))
            except Exception as e:
                print(f"发送消息失败: {str(e)}")
                raise
            
            # 接收响应
            while True:
                try:
                    response = json.loads(await websocket.recv())
                    
                    # 错误处理
                    if response.get("error"):
                        print(f"服务器错误: {response['error']}")
                        st.error(f"服务器错误: {response['error']}")
                        break
                    
                    # 处理响应块
                    chunk = response.get("chunk", "")
                    if chunk:
                        yield chunk
                    
                    # 处理最终消息
                    if response.get("is_final"):
                        if "variables" in response:
                            st.session_state.variables = response["variables"]
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket连接已关闭")
                    break
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    break
                    
    except Exception as e:
        print(f"WebSocket连接错误: {str(e)}")
        raise

# 修改主函数
def main():
    """
    主函数，运行Streamlit应用
    """
    create_chat_interface()
    
    # 加载Orca提示词和变量
    if not hasattr(st.session_state, 'variables') or st.session_state.variables is None:
        orca_content, variables = load_orca_prompt()
        variables["query"] = []
        st.session_state.variables = variables
        st.session_state.orca_content = orca_content
    else:
        variables = st.session_state.variables
        orca_content = st.session_state.orca_content
    
    # 创建输入框
    if user_input := st.chat_input("请输入您的问题...", key=f"chat_input_{st.session_state.conversation_id}"):
        # 添加用户消息到界面
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # 显示助手正在输入的消息
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # 处理响应
            async def process_response():
                full_response = ""
                try:
                    async for chunk in chat_with_backend(user_input):
                        if chunk:
                            print(f"Processing chunk: {chunk}")  # 打印正在处理的块
                            full_response += chunk
                            # 确保立即更新UI
                            message_placeholder.markdown(full_response + "▌")
                            # 强制刷新
                            await asyncio.sleep(0.01)
                    
                    print(f"Final response: {full_response}")  # 打印最终完整响应
                    
                    if full_response:
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        message_placeholder.markdown("抱歉，处理您的请求时出现错误。")
                    
                except Exception as e:
                    print(f"Error in process_response: {e}")  # 打印详细错误信息
                    message_placeholder.markdown(f"处理错误: {str(e)}")
            
            try:
                # 使用asyncio.run运行异步函数
                asyncio.run(process_response())
            except Exception as e:
                st.error(f"运行时错误: {str(e)}")
                message_placeholder.markdown("抱歉，系统出现错误。")

if __name__ == "__main__":
    main()
