from youtube_transcript_api import YouTubeTranscriptApi
import re
# import os
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
# os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:10809'

async def get_video_id(url):
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

async def translate_captions(url):
    """获取YouTube视频字幕并翻译成中文"""
    try:
        # 获取视频ID
        video_id = await get_video_id(url)
        # 获取字幕
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # 拼接字幕
        all_content = ""
        for item in transcript_list:
            all_content += item['text'] + " "
        return all_content

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None

async def get_youtube_caption(video_url='', params_format=False):
    if params_format:
        return ['video_url']
    content = await translate_captions(video_url)
    return content

async def main():
    # 示例用法
    # url = input("请输入YouTube视频URL: ")
    url = "https://www.youtube.com/watch?v=WQQdd6qGxNs"
    captions = await get_youtube_caption(video_url=url)
    
    print(captions)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())