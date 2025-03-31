from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Iterator, Union, List
from .tool import Tool
from Orca.register.config import load_api_key

class GoogleSearchTool(Tool):
    """Google搜索工具"""
    
    name = "google_search"  # 工具名称
    description = "使用Google搜索引擎搜索信息"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "query": {
            "type": "string",
            "description": "搜索内容",
            "required": True
        },
        "search_numbers": {
            "type": "integer",
            "description": "返回结果数量",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "results": {
            "type": "array",
            "description": "搜索结果列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        query = inputs.get("query", "")
        search_numbers = inputs.get("search_numbers", 3)
        
        # 参数校验
        if not query:
            raise Exception("搜索内容不能为空")
        
        try:
            # 获取搜索API密钥
            serp_api_key = load_api_key("serp")
            
            # 设置搜索参数
            params = {
                "engine": "google",
                "q": query,
                "num": search_numbers,
                "api_key": serp_api_key
            }
            
            # 执行搜索
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results["organic_results"]
            
            # 处理搜索结果
            processed_results = await self._process_search_results(organic_results)
            
            return {"results": processed_results}
        except Exception as e:
            raise Exception(f"Google搜索失败: {str(e)}")
    
    async def _process_search_results(self, organic_results: List[Dict]) -> List[str]:
        """处理搜索结果，提取网页内容"""
        processed_results = []
        
        for result in organic_results:
            cur_result = f"《{result['title']}》"
            link = result['link']
            
            try:
                # 发送HTTP请求获取网页内容
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(link, headers=headers, timeout=10)
                response.encoding = response.apparent_encoding
                
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 移除script、style等标签
                for script in soup(['script', 'style']):
                    script.decompose()
                    
                # 获取文本内容    
                text = soup.get_text(separator='\n', strip=True)
                
                # 添加到结果中
                cur_result += f"\n{text}"
            except Exception as e:
                # 如果抓取失败，使用摘要
                cur_result += f"\n{result.get('snippet', '无摘要')}"
                
            processed_results.append(cur_result)
            
        return processed_results 