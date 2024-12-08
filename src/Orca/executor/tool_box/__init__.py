from .web_search import google_search
from .code_execute import code_execute
from .dir_reader import dir_reader
from .save_to_local import save2local

all_tools = {
    "code_execute":{
        "object":code_execute,
        "describe":"代码执行器，需要参数{'code':待执行的代码, 'code_params':需要给代码传递的参数}",
        }, 
    "google_search":{
        "object":google_search,
        "describe":"谷歌搜索，需要参数{'query':搜索内容, 'search_numbers':返回结果数量}",
    },
    "dir_reader":{
        "object":dir_reader,
        "describe":"读取一个文件夹下的全部文件的内容，需要参数{'dirs':待读取的文件夹路径，格式为[dir1, dir22, ...]}",
    },
    "save2local":{
        "object":save2local,
        "describe":"将文本保存至本地，需要参数{'contents':需要保存的内容,'output_path':输出路径}",
    }
    }
