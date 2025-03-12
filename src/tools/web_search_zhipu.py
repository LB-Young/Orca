import requests
import uuid
import json
from load_local_api_keys import load_local_api_keys

async def web_search_zhipu(keyword="", params_format=False):
    """智谱AI网络搜索工具
    keyword: 搜索关键词
    """
    if params_format:
        return ['keyword']
        
    try:
        api_key = load_local_api_keys('zhipu')
        msg = [
            {
                "role": "user",
                "content": keyword
            }
        ]
        tool = "web-search-pro"
        url = "https://open.bigmodel.cn/api/paas/v4/tools"
        request_id = str(uuid.uuid4())
        data = {
            "request_id": request_id,
            "tool": tool,
            "stream": False,
            "messages": msg
        }

        resp = requests.post(
            url,
            json=data,
            headers={'Authorization': api_key},
            timeout=300
        )
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

async def ut():
    res = await web_search_zhipu("中国队奥运会拿了多少奖牌")
    print(res)

if __name__ == '__main__':
    import asyncio
    asyncio.run(ut())
