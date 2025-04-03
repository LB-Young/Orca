"""
bject_1 = None
class Test:
    def __init__(self, value):
        self.value = value
        self.save()
    
    def save(self):
        global object_1
        object_1 = self

test = Test(1)

print(object_1.value)
"""

import time
import asyncio
class Test:
    def __init__(self):
        self.memory = []
        self.compressed_memory = []

    async def add_memory(self, memory):
        self.memory.extend(memory)
        asyncio.create_task(self.compress(memory))

    async def compress(self, memory):
        for item in memory:
            self.compressed_memory.append(item)
            await asyncio.sleep(2)

async def main():
    test = Test()
    await test.add_memory([1, 2, 3, 4, 5])
    for i in range(12):
        print(test.memory)
        print(test.compressed_memory)
        print(f"----------{i}------------")
        await asyncio.sleep(1)
asyncio.run(main())

