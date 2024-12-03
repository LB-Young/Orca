import re


class PromptAnalysis:
    def __init__(self):
        pass
    async def analyze(self, prompt, all_states=None):
        """
        prompt解析：
        1、按步骤切分prompt，给出步骤的type，content，result_variable，all_next_prompt；
        type:["prompt"、"function"、"FOR"、"IF"、"exit"、"bp"、"agent_init"、"function_init"]
        """
        self.prompt = prompt.strip()
        steps_infos = []
        
        # 定义所有结构的正则模式
        patterns = [
            (r'FOR\s+.*?END\s*', 'FOR'),
            (r'IF\s+.*?END\s*', 'IF'), 
            (r'@exit\([^)]*\)\s*', 'exit'),
            (r'@\(bp\)\s*', 'bp'),
            (r'@agent_init\([^)]*\)\s*(->|->>) *[a-zA-Z0-9_]+\s*(?:\((.*?)\))?\s*', 'agent_init'),
            (r'@[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)\s*(->|->>) *[a-zA-Z0-9_]+\s*?(?:\((.*?)\))?\s*', 'function'),
            (r'```\s*.*?```\s*', 'function_init'),
            (r'(?:CODE:\s*)?.*?(->|->>) *[a-zA-Z0-9_]+\s*(?:\((.*?)\))?\s*', 'prompt')
        ]
        
        # 找出所有匹配及其位置
        matches = []
        current_pos = 0
        while current_pos < len(prompt):
            earliest_match = None
            earliest_type = None
            earliest_start = len(prompt)
            
            for pattern, type_ in patterns:
                match = re.compile(pattern, re.DOTALL).search(prompt, current_pos)
                if match and match.start() < earliest_start:
                    # 对于prompt类型,需要额外检查不要匹配到其他结构的内部内容
                    if type_ == 'prompt':
                        # 检查这个位置是否在其他结构内部
                        is_inside = False
                        for m in matches:
                            if match.start() > m['start'] and match.end() < m['end']:
                                is_inside = True
                                break
                        if is_inside:
                            continue
                    earliest_match = match
                    earliest_type = type_
                    earliest_start = match.start()
            
            if earliest_match:
                content = earliest_match.group().strip()
                matches.append({
                    'start': earliest_match.start(),
                    'end': earliest_match.end(),
                    'type': earliest_type,
                    'content': content,
                    'exit': earliest_type == 'exit',
                    'breakpoint': earliest_type == 'bp'
                })
                current_pos = earliest_match.end()
            else:
                break
        
        # 过滤掉被嵌套的匹配
        filtered_matches = []
        for i, current in enumerate(matches):
            is_nested = False
            for j, other in enumerate(matches):
                if i != j and current['start'] > other['start'] and current['end'] < other['end']:
                    is_nested = True
                    break
            if not is_nested:
                filtered_matches.append({
                    'type': current['type'],
                    'content': current['content'],
                    'exit': current['exit'],
                    'breakpoint': current['breakpoint']
                })
        
        return filtered_matches

async def ut():
    prompt_llm_params = """
CODE: 请根据以下内容生成一个json格式的内容：$variable。
并且@name让他继续回答 ->result(json)
```workflow
def flow1():
    @tool1($a) -> result1
    @tool2($result1) -> result2
    return result2
```
@flow1(
    query="请根据以下内容生成一个json格式的内容：$variable。使用chatglm3-130b模型。",
)->result
        """
    prompt_analysis = PromptAnalysis()
    response = await prompt_analysis.analyze(prompt_llm_params)
    print(response)


if __name__ == '__main__':
    import asyncio
    asyncio.run(ut())