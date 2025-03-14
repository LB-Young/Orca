class AgentCallExecutor:
    def __init__(self):
        pass

    async def execute(self, agent_object, agent_input, all_states=None, stream=True):
        if stream:
            agent_response = ""
            response = agent_object.execute(agent_input, all_states=all_states, stream=stream)
            result = {
                "execute_result":{
                    "result":response,
                },
                "all_states":all_states
            }
            return result
        else:
            agent_response = ""
            async for item in agent_object.execute(agent_input, all_states=all_states, stream=stream):
                # print(item, end="", flush=True)
                agent_response += item

            result = {
                "execute_result":{
                    "result":agent_response,
                },
                "all_states":all_states
            }
            return result