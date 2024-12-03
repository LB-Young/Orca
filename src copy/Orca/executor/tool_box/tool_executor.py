from Orca.executor.tool_box import google_search, send_email, get_weather


class ToolExecutor:
    def __init__(self):
        self.tools = {
            "google_search":{
                "type": "function",
                "function": {
                    "name": "google_search",
                    "description": "网页搜索",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "检索的输入",
                            },
                            "num_results": {
                                "type": "string",
                                "description": "检索的网页数目，默认为10",
                            }
                        },
                        "required": ["query"]
                    },
                }
            },
            "send_email": {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "发送邮件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sender_email": {
                                "type": "string",
                                "description": "发送方邮箱号",
                            },
                            "sender_password": {
                                "type": "string",
                                "description": "发送方邮箱密码",
                            },
                            "receiver_email": {
                                "type": "string",
                                "description": "收件方邮箱号",
                            },
                            "subject": {
                                "type": "string",
                                "description": "邮件主题",
                            },
                            "body": {
                                "type": "string",
                                "description": "邮件正文",
                            }
                        },
                        "required": ["sender_email", "sender_password", "receiver_email", "subject", "body"]
                    },
                }
            },
            "get_weather": {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "获取天气",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "待查询城市",
                            }
                        },
                        "required": ["location"]
                    },
                }
            }
        }

    def get_tools(self):
        return self.tools

    async def execute(self, function_name, function_params):
        # Execute the tool
        # Return the result
        if function_name == "google_search":
            response = google_search(function_params['query'], function_params['num_results'])
            return response
        elif function_name == "send_email":
            _ = send_email(function_params["sender_email"], function_params["sender_password"],
                                         function_params["receiver_email"], function_params["subject"],
                                         function_params["body"])
            return "send success"
        elif function_name == "get_weather":
            response = get_weather(function_params["city"])
            return response