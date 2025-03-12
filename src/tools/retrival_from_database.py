import requests
import json

url = "http://127.0.0.1:8013/retrival"

async def retrive_from_database(query="", params_format: bool = False):
    if params_format:
        return ['query']
    request_body = {
        "file_path": "",
        "need_embedding":True,
        "db_name":"tmp",
        "db_type":"local",
        "query": "结构化抽取是什么意思",
        "temperature": 1.0
    }

    response = requests.post(url=url, data=json.dumps(obj=request_body))
    response.encoding = 'utf-8'
    ret = response.json()['answer']
    # print("retrieval finished!")
    return ret