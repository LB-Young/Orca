from Orca.message.base_message import BaseMessage

class AgentMessage(BaseMessage):

    def __init__(self, role: str, content: str, message_type: str, message_from: str, message_to: str):
        self.role = role
        self.content = content
        self.message_type = message_type
        self.message_from = message_from
        self.message_to = message_to

    