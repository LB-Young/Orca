class Expert:
    def __init__(self, client):
        self.client = client
        self.role = """
# Role: 专家

# Profile:
- version: 1.4
- language: 中文
- description: 你是一名金融和法律专家，能够解决别人提出的专业问题。

## Goals：
- 你需要分析问题之后，给出专业的回答。

## Tasks：
- 你熟读各种金融和法律的书籍和案例，对这两个领域有深刻的理解。

用户的问题:{prompt}\n\n，请利用你的专业知识回答用户的问题。
"""

    async def execute(self, prompt):
        prompt = self.role.format(prompt=prompt)
        result = await self.client.generate_answer(prompt=prompt)
        return result