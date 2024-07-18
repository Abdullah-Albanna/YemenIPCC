from . import (
    os,
    Any, logger,
    gettempdir
    )
from .get_system import system

class VariableManager:
    """
    A class to load and save the temporary variables.
    """
    tempdir = gettempdir() if system == "Windows" else os.path.join(os.path.expanduser("~/.cache"))
    
    def __init__(self, filename: str = os.path.join(tempdir, "yemenipcc","yemenipcc_temp_variables.txt")):
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
                    if ":" not in line:
                        continue
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

    def getValidate(self) -> bool:
        """
        Gets the value of the "validate" menubar button
        """

        # Load existing variables from the text file
        try:
            saved_variables = self.loadTempVariables()
        except Exception as e: 
            logger.warning(f"Could not load the saved variables, error:{e}")

        validate = saved_variables.get('validate', "True")
        if validate == "False":
            return False
        elif validate == "True":
            return True
        
    def getRunning(self) -> bool:
        """
        Get the current running state
        """
        # Load existing variables from the text file
        try:
            saved_variables = self.loadTempVariables()
        except Exception as e: 
            logger.warning(f"Could not get the running variable, error:{e}")

        running = saved_variables.get('running', "False")

        if running == "False":
            return False
        elif running == "True":
            return True
        
    def setRunning(self, value: bool) -> None:
        """
        Update the running state and save to the file
        """

        running = value
        # Load existing variables from the text file
        try:
            saved_variables = self.loadTempVariables()
        except Exception as e: 
            logger.warning(f"Could not set the running variable, error:{e}")

        saved_variables['running'] = running
        self.saveVariables(saved_variables)

    def saveVariableInfo(self, variable_name, variable_info) -> None:
        """
        Saves the passed variable_name to the content of variable_info to the temporary file
        """
        # Load existing variables from the text file
        try:
            temp_variables = self.loadTempVariables()
        except Exception as e: 
            logger.warning(f"Could not load the saved variables, error:{e}")

        # Update or add the selected bundle name to the saved variables
        temp_variables[f'{variable_name}'] = variable_info
        
        # Save the updated variables to the text file
        try:
            self.saveVariables(temp_variables)
        except Exception as e: 
            logger.warning(f"Could not save the variables, error:{e}")

    def getVariableInfo(self, variable_name, variable_default) -> str:
        """
        Gets whatever passed variable_name's content, if there is no content or does not exists, then the variable_default is used
        """
        # Load existing variables from the text file
        try:
            temp_variables = self.loadTempVariables()
        except Exception as e: 
            logger.warning(f"Could not load the saved variables, error:{e}")

        return temp_variables.get(variable_name, variable_default)
        