import json
from Orca.segment_executor.llm_client import LLMClient

async def condition_judge(input="", categories=[], all_states=None, params_format=False):
    if params_format:
        return ['input', 'categories']
    try:
        if all_states is None:
            raise Exception("无法使用condition_judge函数，请传入all_states参数！")
        else:
            config_dict = all_states['config'].get_configs()
            llm_client = LLMClient(config_dict)
            return_foramt = '{"类别":"判断结果类别"}'
            prompt = f"""判断以下内容属于哪一个类别：\n内容为：\n{input}\n类别为：\n{categories}\n请输出一个类别，格式为：\n{return_foramt}\n"""
            result = await llm_client.generate_answer(prompt)
            category = json.loads(result)['类别']
            if category in categories:
                return category
            else:
                raise Exception("判断结果不在给定的类别中！")
    except:
        raise Exception("文件夹内容读取出错！")
    
"""
"dir_reader":{
    "object":dir_reader,
    "describe":"读取一个文件夹下的全部文件的内容，需要参数{'dirs':待读取的文件夹路径，格式为[dir1, dir22, ...]}",
}
"""