from youtube_transcript_api import YouTubeTranscriptApi
import re
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class YouTubeCaptionTool(Tool):
    """YouTube字幕提取工具"""
    
    name = "youtube_caption"  # 工具名称
    description = "提取YouTube视频的字幕"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "video_url": {
            "type": "string",
            "description": "YouTube视频URL",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "captions": {
            "type": "string",
            "description": "提取的视频字幕内容"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        video_url = inputs.get("video_url", "")
        
        # 参数校验
        if not video_url:
            raise Exception("视频URL不能为空")
        
        # 提取字幕
        content = await self._translate_captions(video_url)
        return content
    
    async def _get_video_id(self, url):
        """从YouTube URL中提取视频ID"""
        # 支持几种常见的YouTube URL格式
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError("无效的YouTube URL")
    
    async def _translate_captions(self, url):
        """获取YouTube视频字幕并翻译成中文"""
        try:
            # 获取视频ID
            video_id = await self._get_video_id(url)
            # 获取字幕
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # 拼接字幕
            all_content = ""
            for item in transcript_list:
                all_content += item['text'] + " "
            return all_content

        except Exception as e:
            raise Exception(f"获取YouTube字幕失败: {str(e)}") 
