
from .projectimports import (tk, List, os, platform, gettempdir)
from .variables_manager import VariableManager
from .logging_config import setupLogging
import logging


setupLogging(debug=True, file_logging=True)


tempdir = gettempdir() if platform.system() == "Windows" else os.path.join(os.path.expanduser("~/.cache"))


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
    logging.debug(f"changing_option.py - Selected a new bundle option: {selected_bundle}")
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\nSelected {selected_bundle}\n")
        log_text.see(tk.END)
        
    # Load existing variables from the text file
    try:
        temp_variables = VariableManager().loadTempVariables()
    except Exception as e:
        logging.error(f"changing_option.py - Could not load the saved bundle variables, error: {e}")

    # Update or add the selected bundle name to the saved variables
    temp_variables['selected_bundle'] = selected_bundle
    
    # Save the updated variables to the text file
    try:
        VariableManager().saveVariables(temp_variables)
    except Exception as e:
        logging.error(f"changing_option.py - Could not save bundle option, error: {e}")

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
    logging.debug(f"changing_option.py - Selected a new container option: {selected_which_one}")
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\nSelected {selected_which_one}\n")
        log_text.see(tk.END)

    # Load existing variables from the text file
    try:
        saved_variables = VariableManager().loadTempVariables()
    except Exception as e:
        logging.error(f"changing_option.py - Could not load saved container option, error: {e}")
        pass
    # Update or add the selected 'which one' option to the saved variables
    saved_variables['selected_which_one'] = selected_which_one
    
    # Save the updated variables to the text file
    try:
        VariableManager().saveVariables(saved_variables)
    except Exception as e:
        logging.error(f"changing_option.py - Could not save container option, error: {e}")
        pass

    return selected_which_one