import os


async def save2local(contents="", path="", params_format=False):
    if params_format:
        return ['contents', 'path']
    try:
        if len(path) == 0:
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(contents)
            path = "result.txt"
        else:
            path = eval(path)
            with open(path, "w", encoding="utf-8") as f:
                f.write(contents)
        return f"内容已经保存至{path}!"
    except:
        raise Exception("文件夹内容读取出错！")
    
"""
"save2local":{
    "object":save2local,
    "describe":"将文本保存至本地，需要参数{'contents':需要保存的内容,'output_path':输出路径}",
}
"""