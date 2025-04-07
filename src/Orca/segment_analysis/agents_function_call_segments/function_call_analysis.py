import json
import copy
import logging
import inspect
from Orca.utils.string_to_dict import parse_string_to_dict
from Orca.segment_executor.llm_client import LLMClient
from Orca.utils.variable_replace import replace_variable
from Orca.utils.str_2_function import create_function_from_string

logger = logging.getLogger(__name__)

class FunctionCallAnalysis:
    def __init__(self):
        pass
        
    async def analysis(self, pure_prompt: str, all_states: list) -> None:
        all_tools = all_states['tools_agents_pool'].get_tools()
        all_agents = all_states['tools_agents_pool'].get_agents()
        module_name = pure_prompt.strip().split("(")[0].replace("@", "").strip()
        params_content = pure_prompt.split(module_name)[-1].strip()
        raw_params_content = params_content
        if raw_params_content[0] == "(" and raw_params_content[-1] == ")" and "=" in raw_params_content:
            raw_params_content = '{' + raw_params_content[1:-1] + '}'
        if module_name in all_agents.keys():
            if params_content[0] == "(" and params_content[-1] == ")":
                params_content = params_content[1:-1]
            params_content = await replace_variable(params_content, all_states)
            # agent_response = await all_agents[module_name].execute(params_content)
            result = {
                    "analysis_result":{
                        "object":all_agents[module_name]['object'],
                        "params":params_content,
                        "type": "agent"
                    },
                    "all_states":all_states
                }
            return result

        else:
            params_dict = {}
            if params_content[0] == "(" and params_content[-1] == ")" and "=" in params_content:
                params_content = '{' + params_content[1:-1] + '}'
                try:
                    tmp_params_dict = json.loads(params_content)
                except:
                    tmp_params_dict = await parse_string_to_dict(raw_params_content)

                for key, value in tmp_params_dict.items():
                    new_value = await replace_variable(value, all_states)
                    params_dict[key] = new_value

            if len(params_dict) == 0:
                if all_states is None:
                    raise Exception("All_states is None, can not extract function_call params")
                else:
                    self.config_dict = all_states['config'].get_configs()
                    self.llm_client = LLMClient(config_dict=self.config_dict)

                if module_name in all_tools.keys():
                    tools_proerties = {}
                    required_params = []
                    for param_key, param_value in all_tools[module_name]["object"].inputs.items():
                        tools_proerties[param_key] = {
                                    "type": param_value['type'],
                                    "description": param_value['description']
                            }
                        if param_value['required']:
                            required_params.append(param_key)
                    tools = [{
                                "type": "function",
                                "function": {
                                    "name": all_tools[module_name]["object"].name,
                                    "description": all_tools[module_name]["object"].description,
                                    "parameters": {
                                        "type": "object",
                                        "properties": tools_proerties,
                                        "required": required_params
                                    },
                                }
                            }]
                else:
                    raise Exception(f"Can not find tools for {module_name}!")

                extracted_params_prompt = params_content
                message = [{'role': 'user', 'content': "问题："+ extracted_params_prompt + "\n要求：请直接调用工具，不要输出任何解释和反问。"}]
                extracted_params_generator = self.llm_client.generate_answer(messages = message, tools=tools)
                extracted_params = ""
                async for chunk in extracted_params_generator:
                    extracted_params += chunk
                extracted_params = extracted_params.split(":",1)[-1]
                params_dict = json.loads(extracted_params)

                for key, value in params_dict.items():
                    if isinstance(value, str):
                        value = await replace_variable(value, all_states)
                    else:
                        pass
                    params_dict[key] = value
            if isinstance(all_tools[module_name]['object'], str) and all_tools[module_name]['type'] == "python_init":
                all_tools[module_name]['object'] = await create_function_from_string(all_tools[module_name]['object'])
            if isinstance(all_tools[module_name]['object'], str):
                final_result_variable = all_tools[module_name]['object'].rsplit("return", 1)[-1].strip()
                workflow_content = all_tools[module_name]['object'].rsplit("return", 1)[0].strip()
                workflow_content = workflow_content.split("\n",1)[1].strip()
                all_tools[module_name]['object'] = workflow_content
                extracted_params = params_dict
            else:
                module_need_params = all_tools[module_name]['object'].inputs
                extracted_params = {}
                if params_dict == {}:
                    raise Exception("Can not extract params for module_name!")
                for name, param in module_need_params.items():
                    extracted_params[name] = params_dict[name]
            if all_tools[module_name]['type'] == "workflow_init":
                all_states['copy_variables_pool'] = copy.deepcopy(all_states['variables_pool'])
                all_states['variables_pool'].init_variables(extracted_params)
                result = {
                    "analysis_result":{
                        "object":all_tools[module_name]['object'],
                        "params":extracted_params,
                        "type": "workflow_init",
                        "final_result_variable":final_result_variable
                    },
                    "all_states":all_states
                }
            elif all_tools[module_name]['type'] == "function":
                result = {
                    "analysis_result":{
                        "object":all_tools[module_name]['object'],
                        "params":extracted_params,
                        "type": "function"
                    },
                    "all_states":all_states
                }
            elif all_tools[module_name]['type'] == "python_init":
                result = {
                    "analysis_result":{
                        "object":all_tools[module_name]['object'],
                        "params":extracted_params,
                        "type": "python_init"
                    },
                    "all_states":all_states
                }
            return result
            # else:
            #     if all_tools[module_name]['type'] == "function":
            #         result = await all_tools[module_name]['object'](**extracted_params)
            #     elif all_tools[module_name]['type'] == "python_init":
            #         my_func = eval(all_tools[module_name]['function_content'])
            #         result = my_func(**extracted_params)
            #     result = {          
            #         "result":result,
            #         "analysis_result":{},
            #         "executed":True,
            #         "all_states":all_states
            #     }
            # return result


