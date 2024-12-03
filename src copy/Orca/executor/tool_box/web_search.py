import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
load_dotenv()
serp_api_key = os.getenv("SERP_API_KEY")

def google_search(self, query, num_results=10):
    """
    Search Google for a given query and return the top results.

    :param query: The query to search for.
    :param num_results: The number of results to return.
    :return: A list of the top results.
    """
    params = {
    "engine": "google",
    "q": query,
    "num": num_results,
    "api_key": serp_api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results["organic_results"]
    return organic_results



async def ut():
    response = google_search("python")
    print(response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main=ut())