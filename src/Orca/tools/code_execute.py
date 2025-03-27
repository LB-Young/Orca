import json
import asyncio
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class CodeExecuteTool(Tool):
    """代码执行工具"""
    
    name = "code_execute"  # 工具名称
    description = "执行Python代码"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "code": {
            "type": "string",
            "description": "待执行的Python代码",
            "required": True
        },
        "code_params": {
            "type": "object",
            "description": "需要给待执行函数传递的执行参数",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "string",
            "description": "代码执行结果"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        code = inputs.get("code", "")
        code_params = inputs.get("code_params", None)
        
        # 参数校验
        if not code:
            raise Exception("代码不能为空")
        
        try:
            # 检查代码是否包含函数定义
            if code.strip().startswith("def "):
                # 函数执行逻辑
                if "return" in code:
                    return_index = code.rfind("return")
                    split_index = code.find("\n", return_index) 
                    new_code = code[:split_index]
                    params_content = code[split_index:]
                else:
                    new_code = code
                    params_content = None
                    
                my_func = await self._create_function_from_string(new_code)
                try:
                    result = await my_func(**code_params) if code_params else await my_func()
                except Exception as e:
                    raise e
            else:
                # 普通代码片段执行逻辑
                result = await self._execute_code_snippet(code)
                
            return str(result)
        except Exception as e:
            return (f"代码执行器出错:{e}")
    
    async def _create_function_from_string(self, function_string):
        """
        将字符串形式的函数代码转换为可调用的函数对象
        
        Args:
            function_string (str): 包含函数定义的字符串
            
        Returns:
            function: 可调用的函数对象
        """
        # 创建一个新的命名空间来存储函数
        namespace = {}
        
        # 在新的命名空间中执行函数定义
        exec(function_string, namespace)
        
        # 返回创建的函数对象
        function_name = function_string.split("(")[0].split("def ")[1].strip()

        return namespace[function_name]
    
    async def _execute_code_snippet(self, code_snippet):
        """
        执行普通Python代码片段
        
        Args:
            code_snippet (str): 需要执行的Python代码片段
            
        Returns:
            str: 代码执行结果
        """
        # 创建本地命名空间
        local_ns = {}
        
        # 为了捕获最后表达式的值，我们在代码的最后添加一个特殊变量
        modified_code = code_snippet + "\n_result_ = None\n"
        
        # 尝试查找最后一个表达式并将其值赋给_result_
        lines = code_snippet.strip().split('\n')
        if lines:
            last_line = lines[-1].strip()
            # 如果最后一行不是赋值语句或控制流语句，将其视为表达式
            if not (last_line.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'with ')) or 
                    '=' in last_line or last_line.endswith((':',']',')'))):
                # 移除最后一行，并添加_result_赋值
                modified_code = '\n'.join(lines[:-1]) + f"\n_result_ = {last_line}\n"
        
        # 执行代码
        exec(modified_code, {}, local_ns)
        
        # 返回结果
        return local_ns.get('_result_', None)