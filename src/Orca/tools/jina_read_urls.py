import aiohttp
import asyncio
import os
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Iterator, Union, List, Optional
from .tool import Tool

class JinaReadUrlsTool(Tool):
    """Jina URL读取工具"""
    
    name = "jina_read_urls"  # 工具名称
    description = "使用Jina Reader API获取网页内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "urls": {
            "type": "array",
            "description": "待读取的URL列表",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "results": {
            "type": "object",
            "description": "包含URL和对应内容的字典"
        }
    }
    
    # 工具属性
    properties = {}
    
    # 定义缓存目录
    CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
    
    def __init__(self):
        # 确保缓存目录存在
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        urls = inputs.get("urls", [])
        
        # 参数校验
        if not urls:
            raise Exception("URL列表不能为空")
        
        results = {}
        api_key = "jina_96b4defcf63443a6bac47b925e172ab1dyLdulatxXX6jfMjmnTEafMXHxdp"
        
        # 并行处理所有URL
        tasks = [self._fetch_web_content(url, api_key) for url in urls]
        contents = await asyncio.gather(*tasks)
        
        # 将结果组织成字典
        for url, content in zip(urls, contents):
            results[url] = content
        
        return results
    
    def _get_cache_path(self, url: str) -> str:
        """根据URL生成缓存文件路径"""
        # 使用URL的MD5哈希作为文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.CACHE_DIR, f"{url_hash}.json")
    
    async def _read_cache(self, url: str) -> Optional[str]:
        """从缓存中读取内容，如果缓存文件超过24小时则返回None"""
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # 检查缓存是否过期（24小时）
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    current_time = datetime.now()
                    time_diff = current_time - cache_time
                    
                    # 如果缓存未过期，返回内容
                    if time_diff.total_seconds() < 24 * 3600:  # 24小时
                        return cache_data['content']
                    else:
                        print(f"缓存已过期: {url}")
            except Exception as e:
                print(f"读取缓存失败: {str(e)}")
        return None
    
    async def _write_cache(self, url: str, content: str) -> None:
        """将内容写入缓存"""
        cache_path = self._get_cache_path(url)
        try:
            cache_data = {
                'url': url,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入缓存失败: {str(e)}")
    
    async def _fetch_web_content(self, url: str, api_key: Optional[str] = None) -> str:
        """使用Jina Reader API获取网页内容"""
        # 首先尝试从缓存读取
        cached_content = await self._read_cache(url)
        if cached_content is not None:
            return cached_content
    
        # 缓存不存在，从Jina API获取
        jina_url = f"https://r.jina.ai/{url}"
        headers = {}
        if api_key:
            headers["X-API-KEY"] = api_key
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(jina_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        # 将内容保存到缓存
                        await self._write_cache(url, content)
                        return content
                    else:
                        error_msg = f"获取网页内容失败，状态码: {response.status}"
                        try:
                            error_json = await response.json()
                            error_msg += f", 错误信息: {json.dumps(error_json)}"
                        except:
                            pass
                        return error_msg
            except Exception as e:
                return f"获取网页内容时发生错误: {str(e)}" 