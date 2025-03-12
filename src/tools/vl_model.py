from openai import OpenAI
import os
import base64
from load_local_api_keys import load_local_api_keys

async def vl_model(pic_path="", query="", params_format=False):
    try:
        pic_path = eval(pic_path)
    except:
        pass
    if params_format:
        return ['pic_path', "query"]
    
    if not pic_path:
        raise Exception("图片路径不能为空")
    
    # if not os.path.exists(pic_path):
    #     raise Exception("图片不存在")
    
    try:
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
            
        client = OpenAI(
            api_key=load_local_api_keys("aliyun"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        # 判断pic_path是文件还是文件夹
        if os.path.isfile(pic_path):
            base64_image = encode_image(pic_path)

            completion = client.chat.completions.create(
                model="qwen-vl-max-latest",
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "You are a helpful assistant."}]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                            },
                            {"type": "text", "text": f"{query}"},
                        ],
                    }
                ],
            )
            
            return completion.choices[0].message.content
        
        elif os.path.isdir(pic_path):
            # 遍历文件夹中的所有文件
            images_list = []
            for filename in os.listdir(pic_path):
                if filename.split(".")[-1] in ['jpg', 'png', 'jpeg']:
                    base64_image = encode_image(os.path.join(pic_path, filename))
                    images_list.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
                    if len(images_list) > 8:
                        break
            completion = client.chat.completions.create(
                model="qwen-vl-max-latest",
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "You are a helpful assistant."}]
                    },
                    {
                        "role": "user",
                        "content": images_list + [
                            {"type": "text", "text": f"{query}"},
                        ],
                    }
                ],
            )
            
            return completion.choices[0].message.content
        else:
            print("pic_path", pic_path)
            breakpoint()
            raise Exception("输入路径既不是文件也不是文件夹")

    except Exception as e:
        raise Exception(f"视觉语言模型处理失败: {str(e)}")


async def ut():
    pic_path = "/Users/liubaoyang/Desktop/flowchart/tmp/title_0.png"
    res = await vl_model(pic_path)
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(ut())