from typing import Dict, Any, Optional, Iterator, Union
from abc import ABC, abstractmethod

class Tool(ABC):
    """
    工具类，所有工具类必须继承该类

    Args:
        name: str   # 工具名称
        description: str # 工具描述
        inputs: Dict[str, Any] # 工具输入
            - eg: {
                    "name":{
                        "type":"string",
                        "description":"用户名",
                        "required":True
                    },
                    "age":{
                        "type":"integer",
                        "description":"年龄",
                        "required":True
                    }
                }
        outputs: Dict[str, Any] # 工具输出
            - eg: {
                    "info":{
                        "type":"string",
                        "description":"用户其他信息"
                    }
                }
        properties: Dict[str, Any] # 工具的属性，例如：是否需要等待，是否需要用户确认等
            - eg: {
                    "wait":{
                        "type":"boolean",
                        "description":"是否需要等待",
                        "required":True
                    }
                }
    """
    name: str   # 工具名称
    description: str # 工具描述
    inputs: Dict[str, Any] # 工具输入
    outputs: Dict[str, Any] # 工具输出
    properties: Dict[str, Any] # 工具的属性，例如：是否需要等待，是否需要用户确认等

    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        ...

    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        ...
    
    