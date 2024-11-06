class Memory:
    def __init__(self):
        self.memory = []
    
    def init_memory(self, memory=[]):
        self.memory = memory

    def add_memory(self, memory):
        self.memory.append(memory)
    
    def get_memory(self, step=None):
        if step is None:
            return self.memory
        else:
            return_memory = []
            for memory in self.memory:
                if memory['name'] == step:
                    return_memory.append(memory)
            return return_memory