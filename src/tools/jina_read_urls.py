#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
import json
import os
import hashlib
from datetime import datetime

# 定义缓存目录
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(url: str) -> str:
    """根据URL生成缓存文件路径"""
    # 使用URL的MD5哈希作为文件名
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.json")

async def read_cache(url: str) -> Optional[str]:
    """从缓存中读取内容，如果缓存文件超过24小时则返回None"""
    cache_path = get_cache_path(url)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                # 检查缓存是否过期（24小时）
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                current_time = datetime.now()
                time_diff = current_time - cache_time
                
                # 如果缓存未过期，返回内容
                if time_diff.total_seconds() < 10:
                    return cache_data['content']
                else:
                    print(f"缓存已过期: {url}")
        except Exception as e:
            print(f"读取缓存失败: {str(e)}")
    return None

async def write_cache(url: str, content: str) -> None:
    """将内容写入缓存"""
    cache_path = get_cache_path(url)
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

async def fetch_web_content(url: str, api_key: Optional[str] = None) -> str:
    """使用Jina Reader API获取网页内容"""
    # 首先尝试从缓存读取
    cached_content = await read_cache(url)
    if cached_content is not None:
        return cached_content

    # 缓存不存在，从Jina API获取
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "X-Retain-Images": "none",
        "X-Return-Format": "markdown"
    }
    if api_key:
        headers["X-API-KEY"] = api_key
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(jina_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    # 将内容保存到缓存
                    await write_cache(url, content)
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

async def jina_read_urls(urls: List[str], params_format: bool = False) -> Dict[str, Any]:
    """
    从多个URL中提取网页内容
    
    Args:
        urls: 要提取内容的URL列表
        api_key: Jina API密钥（可选）
        params_format: 是否返回参数格式（用于API文档）
    
    Returns:
        Dict[str, Any]: 包含URL和对应内容的字典
    """
    if params_format:
        return ['urls']
    
    results = {}
    api_key = "jina_96b4defcf63443a6bac47b925e172ab1dyLdulatxXX6jfMjmnTEafMXHxdp"
    # 并行处理所有URL
    tasks = [fetch_web_content(url, api_key) for url in urls]
    contents = await asyncio.gather(*tasks)
    
    # 将结果组织成字典
    for url, content in zip(urls, contents):
        results[url] = content
    
    return results

# 用于测试
if __name__ == "__main__":
    async def test():
        urls = ["https://example.com", "https://jina.ai"]
        
        # 记录开始时间
        start_time = datetime.now()
        
        result = await web_content_extractor(urls)
        
        # 计算耗时
        time_cost = (datetime.now() - start_time).total_seconds()
        
        # 打印结果长度和耗时
        print(f"结果长度: {len(result)}")
        print(f"总耗时: {time_cost:.2f}秒")
    
    asyncio.run(test())