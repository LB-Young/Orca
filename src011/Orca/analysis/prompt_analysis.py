import re


class PromptAnalysis:
    def __init__(self, prompt):
        self.prompt = prompt

    async def analyze(self):
        steps_infos = {}
        step_split_pattern = re.compile(pattern=r"(step|步骤)(\s*\w+)\s*[：:]\s*(.*?)(?=step|步骤|$)", flags=re.DOTALL)
        exit_pattern = re.compile(pattern=r"exit\s*\(\s*(?:\s*msg\s*=.*\s*)?")
        breakpoint_pattern = re.compile(pattern=r"(bp)")
        match_steps = step_split_pattern.findall(string=self.prompt)
        print("match_steps:", match_steps)
        index = 0
        for match in match_steps:
            step_info = {}
            step_name = match[1].strip()
            step_content = match[2].strip()
            step_info['index'] = index
            index += 1
            step_info['content'] = step_content
            step_contain_exit = exit_pattern.findall(step_content)
            if len(step_contain_exit) > 0:
                step_info['exit'] = True
            else:
                step_info['exit'] = False
            step_contain_breakpoint = breakpoint_pattern.findall(step_content)
            if len(step_contain_breakpoint) > 0:
                step_info['breakpoint'] = True
            else:
                step_info['breakpoint'] = False
            steps_infos[step_name] = step_info
        return steps_infos

async def ut():
    prompt = '''
    step 1:
    1.1
    1.2
    步骤2:
    2.1
    2.2
    步骤 a:
    3.1
    3.2
    step b:
    4.1
    4.2
    exit()
    '''
    prompt_id_else = """
        step 1:
            query：{query}
            写一首诗
        step 2:
            conditions:
                conflag=llm_tagger({1},['田园诗','边塞诗','其它'])
            if conflag=='田园诗':
                goto  3
            elif  conflag=='边塞诗':
                goto  4
            else:
                goto  5
        step 3:
            exit(msg="写了一首田园诗")
        step 4:
            exit(msg="写了一首边塞诗")
        step 5:
            exit(msg="写了一首其它类型的诗")
        """
    prompt_llm_params = """
        步骤1：
        使用deepseek-chat模型写一首边塞诗

        步骤2：
        用llama3写一首边塞诗

        步骤3：
        用qwen2.5-72b对比{1}和{2}哪个好，并给出理由
        """
    prompt_analysis = PromptAnalysis(prompt_llm_params)
    response = await prompt_analysis.analyze()
    print(response)

if __name__ == '__main__':
    import asyncio
    asyncio.run(ut())