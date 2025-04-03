from typing import List, Dict, Any
from abc import ABC, abstractmethod


class BaseMemory(ABC):

    @abstractmethod
    def add_memory(self, memory: Any):
        pass

    @abstractmethod
    def get_memory(self, last_n: int = 10, compressed: bool = False) -> List[Any]:
        pass

    @abstractmethod
    def clear(self):
        pass


