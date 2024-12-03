import json
class VariablesPool:
    def __init__(self):
        self.variables = {}

    def init_variables(self, variables):
        self.variables = variables

    def add_variable(self, variable_name, variable_value, variable_type):
        if variable_type == "int":
            variable_value = int(variable_value)
        elif variable_type == "json":
            try:
                variable_value = json.loads(variable_value)
            except:
                raise Exception(f"Invalid JSON format, variable: {variable_type}")
        elif variable_type == "list":
            try:
                if "[" in variable_value and "]" in variable_value:
                    variable_value = json.loads(variable_value)
                else:
                    pass
            except:
                raise Exception(f"Invalid list format, variable: {variable_type}")
        else:
            pass
        self.variables[variable_name] = variable_value

    def add_variable_value(self, variable_name, variable_value, variable_type):
        if variable_type == "int":
            variable_value = int(variable_value)
        elif variable_type == "json":
            try:
                variable_value = json.loads(variable_value)
            except:
                raise Exception(f"Invalid JSON format, variable: {variable_type}")
        elif variable_type == "list":
            try:
                if "[" in variable_value and "]" in variable_value:
                    variable_value = json.loads(variable_value)
                else:
                    pass
            except:
                raise Exception(f"Invalid list format, variable: {variable_type}")
        else:
            pass
        if variable_name in self.variables:
            self.variables[variable_name] = self.variables[variable_name].append(variable_value)
        else:
            self.variables[variable_name] = [variable_value]

    def remove_variable(self, variable):
        del self.variables[variable]

    def get_variables(self, variable_name=None):
        if variable_name is None:
            return self.variables
        else:
            return self.variables[variable_name]
