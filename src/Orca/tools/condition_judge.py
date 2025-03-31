import json
from typing import Dict, Any, Iterator, Union
from .tool import Tool
from Orca.segment_executor.llm_client import LLMClient

class ConditionJudgeTool(Tool):
    """条件判断工具"""
    
    name = "condition_judge"  # 工具名称
    description = "判断当前的输入属于哪一个条件类别"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "input": {
            "type": "string",
            "description": "待判断的内容",
            "required": True
        },
        "categories": {
            "type": "array",
            "description": "类别列表",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "category": {
            "type": "string",
            "description": "判断结果类别"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        input_text = inputs.get("input", "")
        categories = inputs.get("categories", [])
        all_states = properties.get("all_states")
        
        # 参数校验
        if not input_text:
            raise Exception("待判断的内容不能为空")
        
        if not categories or not isinstance(categories, list):
            raise Exception("类别列表必须是非空数组")
        
        try:
            if all_states is None:
                raise Exception("无法使用condition_judge函数，请传入all_states参数！")
            else:
                config_dict = all_states['config'].get_configs()
                llm_client = LLMClient(config_dict)
                return_format = '{"类别":"判断结果类别"}'
                prompt = f"""判断以下内容属于哪一个类别：\n内容为：\n{input_text}\n类别为：\n{categories}\n请输出一个类别，格式为：\n{return_format}\n"""
                result = await llm_client.generate_answer(prompt)
                if "```" in result:
                    result = result.replace("```json", "").replace("```", "")
                category = json.loads(result)['类别']
                if category in categories:
                    return {"category": category}
                else:
                    raise Exception("判断结果不在给定的类别中！")
        except Exception as e:
            raise Exception(f"条件判断失败: {str(e)}") 