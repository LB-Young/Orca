import requests
import uuid
import json
import sys
import os
from typing import Dict, Any, Iterator, Union
from .tool import Tool

# 添加src目录到系统路径以导入load_local_api_keys模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Orca.tools.load_local_api_keys import load_local_api_keys

class WebSearchZhipuTool(Tool):
    """智谱AI网络搜索工具"""
    
    name = "web_search_zhipu"  # 工具名称
    description = "使用智谱AI搜索引擎进行网页搜索"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "keyword": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "search_results": {
            "type": "string",
            "description": "搜索结果"
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
        
        # 参数校验
        if not keyword:
            raise Exception("搜索关键词不能为空")
            
        try:
            # 获取API密钥
            api_key = load_local_api_keys('zhipu')
            
            # 构建消息内容
            msg = [
                {
                    "role": "user",
                    "content": keyword
                }
            ]
            
            # 设置API参数
            tool = "web-search-pro"
            url = "https://open.bigmodel.cn/api/paas/v4/tools"
            request_id = str(uuid.uuid4())
            data = {
                "request_id": request_id,
                "tool": tool,
                "stream": False,
                "messages": msg
            }

            # 发送API请求
            resp = requests.post(
                url,
                json=data,
                headers={'Authorization': api_key},
                timeout=300
            )
            
            # 处理响应结果
            all_search = json.loads(resp.content.decode()).get('choices', [])
            all_result = []
            
            for item in all_search:
                try:
                    cur_result = ""
                    for content in item['message']['tool_calls'][1]['search_result']:
                        cur_result += content['content']
                    all_result.append(cur_result)
                except:
                    continue
                    
            return "\n".join(all_result)
            
        except Exception as e:
            raise Exception(f"智谱AI搜索失败: {str(e)}") 