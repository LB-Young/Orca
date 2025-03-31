from bilibili_api import search, video, sync
import asyncio
import json
import os
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class BiliBiliRetrievalTool(Tool):
    """哔哩哔哩视频检索工具"""
    
    name = "bilibili_retrieval"  # 工具名称
    description = "搜索并抓取B站视频字幕"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "keyword": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        },
        "nums": {
            "type": "integer",
            "description": "搜索视频数量",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "videos": {
            "type": "array",
            "description": "包含视频标题和字幕的结果列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        keyword = inputs.get("keyword", "")
        nums = inputs.get("nums", 5)
        
        # 参数校验
        if not keyword:
            raise Exception("搜索关键词不能为空")
        
        # 设置代理（如果需要）
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:80'
        os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:80'
        
        try:
            # 搜索视频
            resp = await search.search_by_type(keyword, search_type=search.SearchObjectType.VIDEO, page=1)
            results = []
            
            # 获取前nums个视频
            for item in resp['result'][:nums]:
                video_id = str(item['bvid'])
                v = video.Video(bvid=video_id)
                
                # 获取字幕
                subtitle_list = await v.get_subtitle(item['id'])
                
                if subtitle_list:
                    # 提取第一个字幕内容
                    subtitle_url = subtitle_list[0]['subtitle_url']
                    subtitle_content = await v.get_subtitle_content(subtitle_url)
                    
                    results.append({
                        'title': item['title'],
                        'subtitle': subtitle_content['body']
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"爬取B站视频字幕失败: {str(e)}") 