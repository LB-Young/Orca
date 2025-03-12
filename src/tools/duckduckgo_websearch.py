from duckduckgo_search import DDGS


async def duckduckgo_websearch(query:str, num_results=5, params_format=False):
    if params_format:
        return ['query', 'num_results']
    results = DDGS().text(query, max_results=num_results)
    
    return results


async def main():
    res = await duckduckgo_websearch(query="manus", num_results=3)
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())