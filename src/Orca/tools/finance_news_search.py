from typing import Dict, Any, Iterator, Union, List
from .tool import Tool
from .finance import cs_news, stcn_news, finance_sina_news

class FinanceNewsSearchTool(Tool):
    """财经新闻搜索工具"""
    
    name = "finance_news_search"  # 工具名称
    description = "搜索关于金融的新闻"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "nums": {
            "type": "integer",
            "description": "搜索的新闻数目",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "news": {
            "type": "array",
            "description": "新闻列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        nums = inputs.get("nums", 50)
        
        # 收集所有新闻
        all_news = []
        
        # 从中国证券报获取新闻
        all_news.extend(await cs_news())
        if len(all_news) >= nums:
            return all_news[:nums]
            
        # 从证券时报获取新闻
        all_news.extend(await stcn_news())
        if len(all_news) >= nums:
            return all_news[:nums]
            
        # 从新浪财经获取新闻
        all_news.extend(await finance_sina_news())
        
        # 返回指定数量的新闻
        return all_news[:nums] 