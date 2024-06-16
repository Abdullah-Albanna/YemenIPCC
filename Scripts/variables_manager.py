import os, platform, tempfile
from typing import Any

# A class to load and save the temporary variables.
class VariableManager:
    tempdir = tempfile.gettempdir() if platform.system() == "Windows" else os.path.join(os.path.expanduser("~/.cache"))
    
    def __init__(self, filename: str = os.path.join(tempdir, "yemenipcc_temp_variables.txt")):
        self.filename = filename
        self.variables = self.loadTempVariables()

    def loadTempVariables(self) -> dict[str, Any]:
        """
        Load temp variables from the text file.
        
        Returns:
            dict: Dictionary containing the loaded variables.
        """
        temp_variables: dict[str, Any] = {}
        try:
            with open(self.filename, "r") as file:
                for line in file:
                    variable_name, variable_value = line.strip().split(":")
                    temp_variables[variable_name] = variable_value.lower() == 'true' if variable_value in ['true', 'false'] else variable_value
        except FileNotFoundError:
            pass
        
        return temp_variables

    def saveVariables(self, variables: dict) -> None:
        """
        Save variables to the text file.
        
        Args:
            variables (dict): Dictionary containing the variables to be saved.
        """
        with open(self.filename, "w") as file:
            for variable_name, variable_value in variables.items():
                file.write(f"{variable_name}:{variable_value}\n")
