import json
import requests
import os
from typing import Dict, Any, Iterator, Union
from .tool import Tool
from Orca.tools.load_local_api_keys import load_local_api_keys

class TwitterSpiderTool(Tool):
    """Twitter爬虫工具"""
    
    name = "twitter_spider"  # 工具名称
    description = "爬取Twitter上的推文内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "keyword": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        },
        "nums": {
            "type": "integer",
            "description": "搜索推文数目",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "tweets": {
            "type": "array",
            "description": "搜索到的推文列表"
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
            
        # 设置代理（根据实际情况可启用）
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
        os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:10809'
            
        try:
            # 创建Twitter API请求
            search_url = "https://api.twitter.com/2/tweets/search/recent"
            
            # 设置查询参数
            query_params = {
                'query': keyword,
                'max_results': nums,
                'tweet.fields': 'created_at,author_id,text'
            }
            
            # 发送请求
            response = requests.get(
                search_url, 
                auth=self._bearer_oauth, 
                params=query_params
            )
            
            if response.status_code != 200:
                raise Exception(f"Twitter API请求失败: {response.status_code} - {response.text}")
                
            # 解析结果
            result = response.json()
            return result
                
        except Exception as e:
            raise Exception(f"爬取Twitter内容失败: {str(e)}")
    
    def _bearer_oauth(self, r):
        """设置Bearer Token验证"""
        bearer_token = load_local_api_keys("twitter_bearer_token")
        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r 