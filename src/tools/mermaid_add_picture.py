import os
from openai import OpenAI
from load_local_api_keys import load_local_api_keys


async def mermaid_add_picture(mermaid_string="", pic_path="", params_format=False):
    if params_format:
        return ['mermaid_string', 'pic_path']
    print("pic_path:", pic_path)
    try:
        pic_path = eval(pic_path)
    except:
        pass

    if os.path.isdir(pic_path):
        tmp_pictures = os.listdir(pic_path)
        pictures = [os.path.join(pic_path, item) for item in tmp_pictures]
    elif os.path.isfile(pic_path):
        pictures = [pic_path]
    else:
        print("pic_path error:", pic_path)
    client = OpenAI(
        api_key=load_local_api_keys("aliyun"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    prompt = f"""
我有一个mermaid流程图：\n{mermaid_string}\n\n我想将本地的部分图片添加到流程图中，本地图片的路径是：\n{pictures}\n\n请把路径中相关的图片链接到对应的节点。\n图片节点的结构为：\nX --> table_n[image: "local_path_to_picture.png"]\n示例说明：表示X节点需要链接一张图片。\n\n结果直接返回添加了图片节点之后的完整的mermaid字符串。
"""
    completion = client.chat.completions.create(
    model="qwen-max-latest", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': prompt}],
    )
    return completion.choices[0].message.content

    

    