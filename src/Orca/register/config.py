import json


class Config:
    def __init__(self):
        self.config = {
            "default_llm_model_name": "",
            "default_model_base_url":"",
            "default_model_api_key":"",
            "default_max_token":5000,
            "default_top_p":0.9,
            "default_temperature":0.95,
            "default_top_k":50,
        }

    def get_configs(self):
        return self.config

    def init_config(self, configs):
        for key, value in configs.items():
            self.config[key] = value
        return
    
def load_api_key(platform):
    with open(r"/Users/liubaoyang/Documents/windows/api_key.json", "r", encoding="utf-8") as f:
        api_dict = json.load(f)
    # print(api_dict)
    return api_dict.get(platform, None)

