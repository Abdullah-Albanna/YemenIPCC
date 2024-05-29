from .projectimports import (tk, List, Any, os, platform, gettempdir)

# Sets the temporary directory to save the also temporary file, which contains the changing variables
tempdir = gettempdir() if platform.system() == "Windows" else os.path.expanduser("~/.cache")

def changeBundle(log_text: tk.Text = None, bundles: List[str] = None, x: tk.IntVar = None) -> str:
    """
    Update the selected bundle based on the user's choice and display a message in the log text.
    
    Args:
        log_text (tk.Text): The text widget to display log messages.
        bundles (List[str]): List of bundle names.
        x (tk.IntVar): The variable representing the selected bundle index.
        
    Returns:
        str: The selected bundle name.
    """
 
    # Gets what you selected
    selected_bundle = bundles[x.get()]
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\nYou selected {selected_bundle}\n")
        
    # Load existing variables from the text file
    saved_variables = VariableManager().loadSavedVariables()
    
    # Update or add the selected bundle name to the saved variables
    saved_variables['selected_bundle'] = selected_bundle
    
    # Save the updated variables to the text file
    VariableManager().saveVariables(saved_variables)
        
    return selected_bundle

def changeWhichOne(log_text: tk.Text = None, which_one: List[str] = None, y: tk.IntVar = None) -> str:
    """
    Update the selected 'which one' option based on the user's choice and display a message in the log text.
    
    Args:
        log_text (tk.Text): The text widget to display log messages.
        which_one (List[str]): List of 'which one' options.
        y (tk.IntVar): The variable representing the selected 'which one' index.
        
    Returns:
        str: The selected 'which one' option.
    """
    selected_which_one = which_one[y.get()]
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\nYou selected {selected_which_one}\n")

    # Load existing variables from the text file
    saved_variables = VariableManager().loadSavedVariables()
    
    # Update or add the selected 'which one' option to the saved variables
    saved_variables['selected_which_one'] = selected_which_one
    
    # Save the updated variables to the text file
    VariableManager().saveVariables(saved_variables)
        
    return selected_which_one

# A class to load and save the temporary variables.
class VariableManager:
    def __init__(self, filename: str = os.path.join(tempdir, "saved_variables.txt")):
        self.filename = filename
        self.variables = self.loadSavedVariables()

    def loadSavedVariables(self) -> dict[str, Any]:
        """
        Load saved variables from the text file.
        
        Returns:
            dict: Dictionary containing the loaded variables.
        """
        saved_variables: dict[str, Any] = {}
        try:
            with open(self.filename, "r") as file:
                for line in file:
                    variable_name, variable_value = line.strip().split(":")
                    saved_variables[variable_name] = variable_value.lower() == 'true' if variable_value in ['true', 'false'] else variable_value
        except FileNotFoundError:
            pass
        
        return saved_variables

    def saveVariables(self, variables: dict) -> None:
        """
        Save variables to the text file.
        
        Args:
            variables (dict): Dictionary containing the variables to be saved.
        """
        with open(self.filename, "w") as file:
            for variable_name, variable_value in variables.items():
                file.write(f"{variable_name}:{variable_value}\n")
