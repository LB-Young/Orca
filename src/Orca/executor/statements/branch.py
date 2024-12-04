import re
from Orca.executor.actions.llm_call import ModelMessage, LLMCall, LLMClient
from Orca.executor.utils.variable_replace import replace_variable

class BranchBlook:
    def __init__(self):
        pass

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

    async def analysis(self, content, all_states=None):
        condition_content_map = await self.parser_branch_content(content=content)
        execute_branch = await self.get_execute_branch(condition_content_map, all_states)
        result = {
            "result":"",
            "analysis_result":{
                "if_content":execute_branch
            },
            "executed":False,
            "all_states":all_states
        }
        return result

    async def get_execute_branch(self, condition_content_map, all_states):
        execute_content = ""
        for condition, content in condition_content_map.items():
            condition = condition.strip()
            if condition.startswith('else'):
                execute_content = content.strip()
                break
            elif condition.startswith('IF'):
                condition = condition[2:-1].strip()
            elif condition.startswith('elif'):
                condition = condition[5:-1].strip()
            full_condition = await replace_variable(condition, all_states)

            if await self.condition_judge(full_condition):
                execute_content = content.strip()
                break
        if execute_content == "":
            raise Exception("无法找到满足条件的分支")
        return execute_content

    async def condition_judge(self, condition_content):
        print("condition_content", condition_content)
        try:
            # 将a替换到条件字符串中，然后执行判断
            result = eval(condition_content)
            print("result", result)
            return result
        except Exception as e:
            # 处理可能的异常
            print(f"Error evaluating condition: {e}")
            print(False)
            return False

    async def parser_branch_content(self, content):
        """
        content:'IF $input == "1": \n    介绍一下gpt4 -> introduction\nelif $input == "2":\n    介绍一下gpt3 -> introduction\nelse:\n    介绍一下gpt2 -> introduction\nEND'
        condition_content_map = {
            "if $input == \"1\":": "介绍一下gpt4 -> introduction",
            "elif $input == \"2\":": "介绍一下gpt3 -> introduction",
            "else:": "介绍一下gpt2 -> introduction"}
        """
        condition_content_map = {}
        # 按行分割内容
        content = content.strip()
        if content.endswith("END"):
            content = content[:-3]
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        current_condition = None
        current_content = []
        
        for line in lines:
                
            # 检查是否是条件语句
            if line.lower().startswith('if ') or line.lower().startswith('elif ') or line.lower() == 'else:':
                # 如果已有条件，保存之前的内容
                if current_condition is not None and current_content:
                    condition_content_map[current_condition] = '\n'.join(current_content)
                    current_content = []
                current_condition = line
            else:
                # 添加内容到当前条件
                current_content.append(line.strip())
        
        # 保存最后一个条件的内容
        if current_condition is not None and current_content:
            condition_content_map[current_condition] = '\n'.join(current_content)
        return condition_content_map

        