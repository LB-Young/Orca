import requests
import json

url = "https://api.siliconflow.cn/v1/chat/completions"

payload = {
    "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "messages": [
        {
            "role": "user",
            "content": "中国大模型行业2025年将会迎来哪些机遇和挑战？"
        }
    ],
    "stream": True,
    "max_tokens": 512,
    "stop": ["null"],
    "temperature": 0.7,
    "top_p": 0.7,
    "top_k": 50,
    "frequency_penalty": 0.5,
    "n": 1,
    "response_format": {"type": "text"},
}
headers = {
    "Authorization": "Bearer sk-vqrdpefdgjjcgsspkfvobagyaglziprtwjmeqcgmdvhnxiwk",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers, stream=True)

# 处理流式响应
for chunk in response.iter_lines():
    if chunk:
        try:
            json_data = json.loads(chunk.decode('utf-8').replace("data: ", ""))
            if 'choices' in json_data and len(json_data['choices']) > 0:
                # 检查是否有 delta 或直接的 content
                delta = json_data['choices'][0].get('delta', {})
                content = delta.get('content', '') or json_data['choices'][0].get('content', '')
                if content:
                    print(content, end='', flush=True)
        except json.JSONDecodeError as e:
            print(f"解析错误: {chunk.decode('utf-8')}")
            continue

print()

