import requests
from typing import Dict, Any, Optional

def jina_search(query: str, 
                num: int = 3, 
                page: int = 1, 
                params_format: bool = False) -> Dict[str, Any]:
    if params_format:
        return ['query', 'num', 'page']
    """
    使用Jina AI进行搜索
    
    Args:
        query (str): 搜索查询词
        gl (str, optional): 地理位置代码. 默认为 "US"
        hl (str, optional): 语言代码. 默认为 "en"
        num (int, optional): 返回结果数量. 默认为 10
        page (int, optional): 页码. 默认为 1
    
    Returns:
        Dict[str, Any]: 搜索结果
    """
    headers = {
        "Authorization": "Bearer jina_96b4defcf63443a6bac47b925e172ab1dyLdulatxXX6jfMjmnTEafMXHxdp",
        "Content-Type": "application/json",
        "X-Retain-Images": "none",
        'X-Respond-With': 'no-content'
    }

    data = {
        "q": query,
        "gl": "US",
        "hl": "en",
        "num": str(num),
        "page": str(page)
    }

    try:
        response = requests.post('https://s.jina.ai/', headers=headers, json=data)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def main():
    """
    主函数，用于测试搜索功能
    """
    # 测试搜索
    result = jina_search("Jina AI")
    breakpoint()
    print(result)

if __name__ == "__main__":
    main()