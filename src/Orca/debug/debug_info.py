class DebugInfo:
    def __init__(self):
        self.debug_info = []
    
    def init_debug_info(self, debug_info=[]):
        self.debug_info = debug_info

    def add_debug_info(self, debug_info):
        self.debug_info.append(debug_info)
    
    def get_debug_info(self, step=None):
        if step is None:
            return self.debug_info
        else:
            return_debug_info = []
            for debug_info in self.debug_info:
                if debug_info['step'] == step:
                    return_debug_info.append(debug_info)
            return return_debug_info
    
    def get_debug_infos(self):
        return self.debug_info