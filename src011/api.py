import os
import json

def set_api_key():
    with open(r"C:\Users\86187\Desktop\api_key.json", "r", encoding="utf-8") as f:
        api_dict = json.load(f)
    os.environ['DEFAULT_MODEL_API_KEY'] = api_dict['deepseek']
    os.environ['DEEPSEEK_CHAT_MODEL_API_KEY'] = api_dict['deepseek']
    os.environ['Groq_API_KEY'] = api_dict['groq']
    os.environ['Together_API_KEY'] = api_dict['together']