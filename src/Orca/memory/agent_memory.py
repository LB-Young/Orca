from typing import List, Any, Union
from Orca.memory.base_memory import BaseMemory
from Orca.message.agent_message import AgentMessage


class AgentMemory(BaseMemory):
    def __init__(self):
        super().__init__()
        self.memory = []
        self.memory_type = "agent"
        self.compressed_memory = []

    async def add_memory(self, message: Union[AgentMessage, List[AgentMessage]]):
        if isinstance(message, AgentMessage):
            self.memory.append(message)
            compressed_memory = await self.compress(message)
            self.compressed_memory.append(compressed_memory)
        else:
            for cur_message in message:
                self.memory.append(cur_message)
                compressed_memory = await self.compress(cur_message)
                self.compressed_memory.append(compressed_memory)

    async def get_memory(self, last_n: int = -1, compressed: bool = False) -> List[Any]:
        if compressed:
            if last_n == -1:
                return self.compressed_memory
            else:
                return self.compressed_memory[-last_n:]
        else:
            if last_n == -1:
                return self.memory
            else:
                return self.memory[-last_n:]

    async def clear(self):
        self.memory = []
        self.compressed_memory = []

    async def compress(self, message: AgentMessage):
        compressed_message = message
        return compressed_message
