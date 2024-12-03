from .executor.tool_box import code_execute, google_search
from Orca.Orca import OrcaExecutor

all_tools = {
    "code_execute":{
        "object":code_execute,
        "describe":"代码执行器，需要参数{'code':待执行的代码, 'code_params':需要给代码传递的参数}",
        }, 
    "google_search":{
        "object":google_search,
        "describe":"谷歌搜索，需要参数{'query':搜索内容, 'search_numbers':返回结果数量}",
    }
    }

__all__ = ["OrcaExecutor", "all_tools"]