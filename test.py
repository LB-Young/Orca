import requests

url = 'https://r.jina.ai/https://www.aishu.cn/cn/'
headers = {
    "Authorization": "Bearer jina_96b4defcf63443a6bac47b925e172ab1dyLdulatxXX6jfMjmnTEafMXHxdp",
    "X-Retain-Images": "none",
    "X-Return-Format": "markdown"
}

response = requests.get(url, headers=headers)

print(response.text)
