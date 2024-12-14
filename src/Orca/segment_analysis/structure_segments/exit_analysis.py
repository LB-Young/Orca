from Orca.utils.variable_replace import replace_variable


class ExitAnalysis:
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
            "analysis_result":{
                "result":exit_message,
            }, 
            "all_states":all_states
        }
        return result