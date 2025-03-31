import os
from youtube_transcript_api import YouTubeTranscriptApi
import json
from typing import Dict, Any, Iterator, Union
from .tool import Tool
from Orca.tools.load_local_api_keys import load_local_api_keys

class YouTubeRetrievalTool(Tool):
    """YouTube视频检索工具"""
    
    name = "youtube_retrieval"  # 工具名称
    description = "爬取YouTube视频字幕和评论"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "keyword": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        },
        "nums": {
            "type": "integer",
            "description": "搜索视频数目",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "videos": {
            "type": "array",
            "description": "包含视频标题、ID、字幕和评论的结果列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:

        from googleapiclient.discovery import build
        # 从输入中提取参数
        keyword = inputs.get("keyword", "")
        nums = inputs.get("nums", 1)
        
        # 参数校验
        if not keyword:
            raise Exception("搜索关键词不能为空")
            
        # 设置代理（根据实际情况可启用）
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
        os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:10809'
            
        try:
            # YouTube API密钥
            YOUTUBE_API_KEY = load_local_api_keys('google_youtube_api')
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            
            # 搜索视频
            search_response = youtube.search().list(
                q=keyword,
                part='id,snippet',
                maxResults=nums
            ).execute()
            
            results = []
            
            for item in search_response['items']:
                if item['id'].get('videoId'):
                    video_id = item['id']['videoId']
                    
                    # 获取字幕
                    try:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        subtitle_text = " ".join([t['text'] for t in transcript])
                    except Exception as e:
                        subtitle_text = f"无字幕 (错误: {str(e)})"
                        
                    # 获取评论
                    try:
                        comments = []
                        comments_response = youtube.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            maxResults=10
                        ).execute()
                        
                        for comment in comments_response['items']:
                            comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                            comments.append(comment_text)
                    except Exception as e:
                        comments = [f"无评论 (错误: {str(e)})"]
                    
                    results.append({
                        'title': item['snippet']['title'],
                        'video_id': video_id, 
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'subtitle': subtitle_text,
                        'comments': comments
                    })
                    
            return results
            
        except Exception as e:
            raise Exception(f"爬取YouTube视频失败: {str(e)}") 