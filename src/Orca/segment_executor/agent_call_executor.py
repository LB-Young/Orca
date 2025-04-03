from Orca.message.agent_message import AgentMessage

class AgentCallExecutor:
    def __init__(self):
        pass

    async def execute(self, agent_object, agent_input, all_states=None, stream=True):
        # 将agent_input中的消息转换为AgentMessage对象
        processed_messages = []
        for msg in agent_input:
            # 创建AgentMessage对象
            agent_msg = AgentMessage(
                role=msg['role'],
                content=msg['content'],
                message_type='user' if msg['role'] == 'user' else 'assistant',
                message_from=msg['role'],
                message_to='assistant' if msg['role'] == 'user' else 'user'
            )
            processed_messages.append(agent_msg)
        
        if stream:
            agent_response = ""
            response = agent_object.execute(processed_messages, all_states=all_states, stream=stream)
            result = {
                "execute_result":{
                    "result":response,
                },
                "all_states":all_states
            }
            return result
        else:
            agent_response = ""
            async for item in agent_object.execute(processed_messages, all_states=all_states, stream=stream):
                # print(item, end="", flush=True)
                agent_response += item

            result = {
                "execute_result":{
                    "result":agent_response,
                },
                "all_states":all_states
            }
            return result