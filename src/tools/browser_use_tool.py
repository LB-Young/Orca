import asyncio
import json
import time
from typing import Optional, Dict, Any

from browser_use import Browser as BrowserUseBrowser
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.dom.service import DomService
from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo


async def BrowserUseTool(action: str = "",
                  url: Optional[str] = None,
                  index: Optional[int] = None, 
                  text: Optional[str] = None,
                  script: Optional[str] = None,
                  scroll_amount: Optional[int] = None,
                  tab_id: Optional[int] = None,
                  params_format: bool = False,
                  **kwargs: Any) -> Dict[str, Any]:
    """
    浏览器自动化工具，可执行多种浏览器操作
    
    Args:
        action: 要执行的浏览器操作，包括：
            - 'navigate': 导航到指定URL
            - 'click': 点击指定索引的元素
            - 'input_text': 在指定元素中输入文本
            - 'screenshot': 捕获屏幕截图
            - 'get_html': 获取页面HTML内容
            - 'execute_js': 执行JavaScript代码
            - 'scroll': 滚动页面
            - 'switch_tab': 切换到指定标签页
            - 'new_tab': 打开新标签页
            - 'close_tab': 关闭当前标签页
            - 'refresh': 刷新当前页面
        url: 用于'navigate'或'new_tab'操作的URL
        index: 用于'click'或'input_text'操作的元素索引
        text: 用于'input_text'操作的文本
        script: 用于'execute_js'操作的JavaScript代码
        scroll_amount: 用于'scroll'操作的滚动像素数（正数向下，负数向上）
        tab_id: 用于'switch_tab'操作的标签页ID
        params_format: 是否返回参数格式
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    if params_format:
        return ['action', 'url', 'index', 'text', 'script', 'scroll_amount', 'tab_id']
    
    # 创建全局变量来存储浏览器实例和上下文
    global _browser, _context, _dom_service, _lock
    
    # 初始化锁（如果尚未初始化）
    if not '_lock' in globals():
        _lock = asyncio.Lock()
    
    async def _ensure_browser_initialized():
        """确保浏览器和上下文已初始化"""
        global _browser, _context, _dom_service
        
        if '_browser' not in globals() or _browser is None:
            _browser = BrowserUseBrowser(BrowserConfig(headless=False))
        
        if '_context' not in globals() or _context is None:
            _context = await _browser.new_context()
            _dom_service = DomService(await _context.get_current_page())
        
        return _context
    
    async with _lock:
        try:
            context = await _ensure_browser_initialized()
            
            if action == "navigate":
                if not url:
                    return {"error": "URL是'navigate'操作所必需的"}
                await context.navigate_to(url)
                time.sleep(5)
                return {"output": f"已导航至 {url}"}
            
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
                element = await context.get_dom_element_by_index(index)
                if not element:
                    return {"error": f"未找到索引为{index}的元素"}
                await context._input_text_element_node(element, text)
                return {"output": f"已在索引为{index}的元素中输入'{text}'"}
            
            elif action == "screenshot":
                screenshot = await context.take_screenshot(full_page=True)
                return {"output": f"已捕获截图（base64长度：{len(screenshot)}）", "system": screenshot}
            
            elif action == "get_html":
                html = await context.get_page_html()
                truncated = html[:2000] + "..." if len(html) > 2000 else html
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
                global _context, _dom_service, _browser
                if '_context' in globals() and _context is not None:
                    await _context.close()
                    _context = None
                    _dom_service = None
                
                if '_browser' in globals() and _browser is not None:
                    await _browser.close()
                    _browser = None
                return {"output": "已清理浏览器资源"}
            
            else:
                return {"error": f"未知操作：{action}"}
        
        except Exception as e:
            return {"error": f"浏览器操作'{action}'失败：{str(e)}"}


# 同步包装函数，用于兼容非异步环境
def BrowserUseToolSync(action: str,
                      url: Optional[str] = None,
                      index: Optional[int] = None,
                      text: Optional[str] = None,
                      script: Optional[str] = None,
                      scroll_amount: Optional[int] = None,
                      tab_id: Optional[int] = None,
                      params_format: bool = False) -> Dict[str, Any]:
    """
    BrowserUseTool的同步包装函数，用于在非异步环境中调用
    """
    if params_format:
        return ['action', 'url', 'index', 'text', 'script', 'scroll_amount', 'tab_id']
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        BrowserUseTool(
            action=action,
            url=url,
            index=index,
            text=text,
            script=script,
            scroll_amount=scroll_amount,
            tab_id=tab_id
        )
    )


if __name__ == "__main__":
    # 测试浏览器工具
    import asyncio
    
    async def test_browser():
        # 导航到百度
        result = await BrowserUseTool(action="navigate", url="https://www.baidu.com")
        print("导航到百度首页结果:", result)
        
        # 使用JavaScript点击新闻按钮
        # 通过选择器查找并点击新闻链接
        js_script = """
        // 查找包含"新闻"文本的链接并点击
        const newsLinks = Array.from(document.querySelectorAll('a')).filter(a => a.textContent.includes('新闻'));
        let clicked = false;
        if (newsLinks.length > 0) {
            newsLinks[0].click();
            clicked = true;
        }
        clicked;
        """
        result = await BrowserUseTool(action="execute_js", script=js_script)
        print("点击新闻按钮结果:", result)
        
        # 等待页面加载（使用JavaScript等待2秒）
        await asyncio.sleep(2)
        
        # 获取点击后的页面状态
        state = await BrowserUseTool(action="get_state")
        print("点击后页面状态:", state)
        
        # 获取页面截图
        screenshot = await BrowserUseTool(action="screenshot")
        print("截图结果:", screenshot.get("output", ""))
        
        # 清理资源
        await BrowserUseTool(action="cleanup")
    
    # 运行测试
    asyncio.run(test_browser())
    
    # 测试同步版本
    # result = BrowserUseToolSync(action="navigate", url="https://www.baidu.com")
    # print(result)
    # state = BrowserUseToolSync(action="get_state")
    # print(state)
    # BrowserUseToolSync(action="cleanup")
