import re
from Orca.executor.actions.llm_call import ModelMessage, LLMCall, LLMClient



class BranchBlook:
    def __init__(self, variable_tool_pool=None, config=None, memories=None, debug_infos=None):
        self.memories = memories
        self.variable_tool_pool = variable_tool_pool
        self.debug_infos = debug_infos
        self.config = config
        self.config_dict = config.get_config()
        self.llm_client = LLMClient(config_dict=self.config_dict)
        self.llm_call = LLMCall(self.variable_tool_pool, self.config, self.memories, self.debug_infos)

    def validate(self, content):
        pass

    def llm_tagger(self, step_output, tag_list):
        tag_list_text = ''
        for i in range(len(tag_list)):
            tag_list_text += f'[{i + 1}]'
            tag_list_text += tag_list[i]
            tag_list_text += '\n'
        prompt = f"请判断【待判断内容】的含义与【候选内容中】的哪个更接近的，并只输出更接近内容的[序号]，不要生成任何解释。\n 【待判断内容】：{step_output}\n 【候选内容】：{tag_list_text}。\n直接输出候选内容的序号:"
        messages = [ModelMessage(role="user", content=prompt)]
        llm_result = self.llm_client.chat(messages)
        n = len(tag_list)
        int_result = [0] * n  # 初始化结果列表，长度为n，所有元素初始为0
        for i in range(1, n + 1):
            if str(i) in llm_result:
                int_result[i - 1] = 1
        if sum(int_result) != 1:
            raise Exception(
                f'llm_tagger_error\nllm_tagger({step_output},{tag_list})的结果为{llm_result})，无法映射到对应类别')
        else:
            tag_result = tag_list[int_result.index(1)]
        return tag_result

    async def execute(self, content, variable):
        lines = content.split('\n')
        modified_lines= [
            line.lstrip() if line.lstrip().startswith('if') or line.lstrip().startswith('else') or line.lstrip().startswith('elif') else line  
            for line in lines
        ]
        content='\n'.join(modified_lines)
        var_name = self.variable_tool_pool.list_variables()
        var_value = []
        step_memory_all = self.memories.get_all_memory()
        step_name = []
        step_output = []
        for i in range(len(step_memory_all)):
            step_name.append(step_memory_all[i]['step'])
            step_output.append(step_memory_all[i]['output'])
        for i in range(len(var_name)):
            var_value.append(self.variable_tool_pool.get_variable(var_name[i]))
        pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*|\d+)\}"

        replaces = [['conditions:', 'if True:'], ['goto', 'step_label=']]
        matches = re.findall(pattern, content)
        for match in matches:
            if match.isdigit():
                if match not in step_name:
                    raise Exception(f"error:step {match} not exist")
                else:
                    replaces.append(["{" + str(match) + "}", f"step_{match}_output"])
            else:
                if match in step_name:
                    replaces.append(["{" + str(match) + "}", f"step_{match}_output"])
                elif match in var_name:
                    replaces.append(["{" + str(match) + "}", f"{match}"])
                else:
                    raise Exception("error:step " + match + " or variable " + match + "not exist")
        for replace in replaces:
            content = content.replace(replace[0], replace[1])
        pattern = r'output(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+'
        matches = re.findall(pattern, content)
        for match in matches:
            dot_indexs=[i for i, char in enumerate(match) if char == '.']
            dot_num=len(dot_indexs)
            if dot_num>0:
                replace_str=""
                replace_str=match[:dot_indexs[0]]+"['"+match[dot_indexs[0]+1:]
                replace_str=replace_str.replace(".","']['")
                replace_str+="']"
                content = content.replace(match,replace_str)
        local_vars = {}
        func_and_var = {'llm_tagger': self.llm_tagger}
        for i in range(len(var_name)):
            func_and_var[f'{var_name[i]}'] = var_value[i]
        for i in range(len(step_name)):
            func_and_var[f'step_{step_name[i]}_output'] = step_memory_all[i]['output']
        exec(content, func_and_var, local_vars)
        step_label = str(local_vars.get('step_label'))
        return "", step_label

