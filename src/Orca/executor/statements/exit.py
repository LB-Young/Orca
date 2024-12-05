from Orca.executor.utils.variable_replace import replace_variable


class ExitBlock:
    def __init__(self):
        pass

    async def analysis(self, content, all_states=None):
        exit_message = ""
        content = await replace_variable(content, all_states)
        content = content.strip().replace("@exit", "").strip()[1:-1].strip()
        if len(content) == 0:
            exit_message = ""
        else:
            message = content.split("=", 1)[1].strip()
            exit_message = message
        result = {
            "result":exit_message,
            "analysis_result":{},
            "executed":True,
            "all_states":all_states
        }
        return result