from Orca.register.config import load_api_key
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup

async def google_search(query='', search_numbers=3, params_format=False):
    """
    Search Google for a given query and return the top results.

    :param query: The query to search for.
    :param num_results: The number of results to return.
    :return: A list of the top results.
    """
    if params_format:
        return ['query', 'search_numbers']
    
    serp_api_key = load_api_key("serp")
    params = {
    "engine": "google",
    "q": query,
    "num": search_numbers,
    "api_key": serp_api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results["organic_results"]
    processed_result = await google_search_process(organic_results)
    return processed_result

async def google_search_process(organic_results):
    processed_results = []
    for result in organic_results:
        cur_result = f"《{result['title']}》"
        link = result['link']
        try:
            # 发送HTTP请求获取网页内容
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(link, headers=headers, timeout=10)
            response.encoding = response.apparent_encoding
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            # 提取正文内容
            # 移除script、style等标签
            for script in soup(['script', 'style']):
                script.decompose()
            # 获取文本内容    
            text = soup.get_text(separator='\n', strip=True)
            # 添加到结果中
            cur_result += f"\n{text}"
        except Exception as e:
            cur_result += f"{result['snippet']}"
        processed_results.append(cur_result)
    return processed_results


async def ut():
    response = await google_search("RAG", "3")
    print(response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main=ut())