from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseMessage(ABC):
    role: str
    content: str
    message_type: str
    message_from: str
    message_to: str
    