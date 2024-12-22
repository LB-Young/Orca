import os


async def save2local(contents="", output_path="", params_format=False):
    if params_format:
        return ['contents', 'output_path']
    try:
        if len(output_path) == 0:
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(contents)
            output_path = "result.txt"
        else:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(contents)
        return f"内容已经保存至{output_path}!"
    except:
        print("contents:", contents)
        print("output_path:", output_path)
        raise Exception("文件夹内容读取出错！")
    
"""
"save2local":{
    "object":save2local,
    "describe":"将文本保存至本地，需要参数{'contents':需要保存的内容,'output_path':输出路径}",
}
"""

if __name__ == "__main__":
    import asyncio
    res = asyncio.run(save2local("test", "F:/logs/orca/output/paper_recommend/Agent_1221.txt"))
    print(res)