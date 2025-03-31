import asyncio
import json
import time
from typing import Optional, Dict, Any, Iterator, Union

from browser_use import Browser as BrowserUseBrowser
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.dom.service import DomService
from .tool import Tool

"""要执行的浏览器操作，包括：'navigate': 导航到指定URL;'input_text': 在指定元素中输入文本;'click': 点击页面元素; 'screenshot': 捕获屏幕截图;'get_html': 获取页面HTML内容;'execute_js': 执行JavaScript代码; 'scroll': 滚动页面;'switch_tab': 切换到指定标签页;'new_tab': 打开新标签页;'close_tab': 关闭当前标签页;'refresh': 刷新当前页面"""
class BrowserUseTool(Tool):
    """浏览器自动化工具"""
    
    name = "browser_use"  # 工具名称
    description = """浏览器自动化工具，可执行多种浏览器操作，浏览器一开始默认打开一个空页面，使用完毕后请关闭浏览器。"""  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "action": {
            "type": "string",
            "description": "要执行的浏览器操作，包括：'navigate': 导航到指定URL;'input_text': 在指定元素中输入文本;'click': 点击页面元素; ''get_html': 获取页面HTML内容;'execute_js': 执行JavaScript代码; 'scroll': 滚动页面;'switch_tab': 切换到指定标签页;'new_tab': 打开新标签页;'close_tab': 关闭当前标签页;'refresh': 刷新当前页面",
            "required": True
        },
        "url": {
            "type": "string",
            "description": "用于'navigate'或'new_tab'操作的URL",
            "required": False
        },
        "index": {
            "type": "integer",
            "description": "用于'click'或'input_text'操作的元素索引",
            "required": False
        },
        "text": {
            "type": "string",
            "description": "用于'input_text'操作的文本",
            "required": False
        },
        "script": {
            "type": "string",
            "description": "用于'execute_js'操作的JavaScript代码",
            "required": False
        },
        "scroll_amount": {
            "type": "integer",
            "description": "用于'scroll'操作的滚动像素数（正数向下，负数向上）",
            "required": False
        },
        "tab_id": {
            "type": "integer",
            "description": "用于'switch_tab'操作的标签页ID",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "output": {
            "type": "string",
            "description": "操作结果"
        }
    }
    
    # 工具属性
    properties = {}
    
    # 全局变量
    _browser = None
    _context = None
    _dom_service = None
    _lock = None
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        action = inputs.get("action", "")
        url = inputs.get("url")
        index = inputs.get("index")
        text = inputs.get("text")
        script = inputs.get("script")
        scroll_amount = inputs.get("scroll_amount")
        tab_id = inputs.get("tab_id")
        
        # 初始化锁（如果尚未初始化）
        if not self._lock:
            self._lock = asyncio.Lock()
        
        async with self._lock:
            try:
                context = await self._ensure_browser_initialized()
                
                if action == "navigate":
                    if not url:
                        return {"error": "URL是'navigate'操作所必需的"}
                    try:
                        # 添加重试逻辑
                        max_retries = 3
                        for retry in range(max_retries):
                            try:
                                await context.navigate_to(url)
                                state = await context.get_state()
                                elements_string = state.element_tree.clickable_elements_to_string()
                                return {"output": f"已导航至 {url}。\n新页面可交互元素: {elements_string}"}
                            except Exception as e:
                                if retry < max_retries - 1:
                                    print(f"导航到 {url} 失败，正在重试 ({retry+1}/{max_retries}): {e}")
                                    await asyncio.sleep(1)  # 在重试前等待
                                else:
                                    raise  # 最后一次重试仍然失败时抛出异常
                    except Exception as e:
                        # 如果所有重试都失败，记录详细错误并返回错误信息
                        error_msg = f"导航到 {url} 失败: {str(e)}"
                        print(error_msg)
                        return {"error": error_msg}
                
                elif action == "click":
                    if index is None:
                        return {"error": "索引是'click'操作所必需的"}
                    element = await context.get_dom_element_by_index(index)
                    if not element:
                        return {"error": f"未找到索引为{index}的元素"}
                    download_path = await context._click_element_node(element)
                    output = f"已点击索引为{index}的元素"
                    if download_path:
                        output += f" - 已下载文件至 {download_path}"
                    return {"output": output}
                
                elif action == "input_text":
                    if index is None or not text:
                        return {"error": "索引和文本是'input_text'操作所必需的"}
                    try:
                        # 先获取页面状态，检查元素是否存在
                        state = await context.get_state()
                        elements_string = state.element_tree.clickable_elements_to_string()
                        print(f"可交互元素: {elements_string}")
                        
                        element = await context.get_dom_element_by_index(index)
                        if not element:
                            return {"error": f"未找到索引为{index}的元素"}
                        
                        await context._input_text_element_node(element, text)
                        return {"output": f"已在索引为{index}的元素中输入'{text}'"}
                    except Exception as e:
                        error_msg = f"在元素{index}中输入文本失败: {str(e)}"
                        print(error_msg)
                        return {"error": error_msg}
                
                elif action == "screenshot":
                    screenshot = await context.take_screenshot(full_page=True)
                    return {"output": f"已捕获截图（base64长度：{len(screenshot)}）", "system": screenshot}
                
                elif action == "get_html":
                    html = await context.get_page_html()
                    state = await context.get_state()
                    elements_string = state.element_tree.clickable_elements_to_string()
                    truncated = f"当前页面可交互元素: {elements_string}\n\n" + "当前页面HTML内容: " + html[:2000] + "..." if len(html) > 2000 else html
                    return {"output": truncated}
                
                elif action == "execute_js":
                    if not script:
                        return {"error": "脚本是'execute_js'操作所必需的"}
                    result = await context.execute_javascript(script)
                    return {"output": str(result)}
                
                elif action == "scroll":
                    if scroll_amount is None:
                        return {"error": "滚动量是'scroll'操作所必需的"}
                    await context.execute_javascript(f"window.scrollBy(0, {scroll_amount});")
                    direction = "下" if scroll_amount > 0 else "上"
                    return {"output": f"已向{direction}滚动{abs(scroll_amount)}像素"}
                
                elif action == "switch_tab":
                    if tab_id is None:
                        return {"error": "标签页ID是'switch_tab'操作所必需的"}
                    await context.switch_to_tab(tab_id)
                    return {"output": f"已切换到标签页{tab_id}"}
                
                elif action == "new_tab":
                    if not url:
                        return {"error": "URL是'new_tab'操作所必需的"}
                    await context.create_new_tab(url)
                    return {"output": f"已打开带有URL {url}的新标签页"}
                
                elif action == "close_tab":
                    await context.close_current_tab()
                    return {"output": "已关闭当前标签页"}
                
                elif action == "refresh":
                    await context.refresh_page()
                    return {"output": "已刷新当前页面"}
                
                elif action == "get_state":
                    state = await context.get_state()
                    state_info = {
                        "url": state.url,
                        "title": state.title,
                        "tabs": [tab.model_dump() for tab in state.tabs],
                        "interactive_elements": state.element_tree.clickable_elements_to_string(),
                    }
                    return {"output": json.dumps(state_info)}
                
                elif action == "cleanup":
                    if self._context is not None:
                        await self._context.close()
                        self._context = None
                        self._dom_service = None
                    
                    if self._browser is not None:
                        await self._browser.close()
                        self._browser = None
                    return {"output": "已清理浏览器资源"}
                
                else:
                    return {"error": f"未知操作：{action}"}
            
            except Exception as e:
                return {"error": f"浏览器操作'{action}'失败：{str(e)}"}
    
    async def _ensure_browser_initialized(self):
        """确保浏览器和上下文已初始化"""
        
        if self._browser is None:
            # 使用默认配置，只保留支持的参数
            browser_config = BrowserConfig(headless=False)
            self._browser = BrowserUseBrowser(browser_config)
        
        if self._context is None:
            try:
                self._context = await self._browser.new_context()
                page = await self._context.get_current_page()
                self._dom_service = DomService(page)
            except Exception as e:
                print(f"初始化上下文或DomService时出错: {e}")
                # 尝试创建新的上下文和页面
                self._context = await self._browser.new_context()
                page = await self._context.new_page()
                self._dom_service = DomService(page)
        
        return self._context 