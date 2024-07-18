
from . import (
    tk, os, 
    List, logger,
    gettempdir
    )
from .variables_manager import VariableManager
from .get_system import system



tempdir = gettempdir() if system == "Windows" else os.path.join(os.path.expanduser("~/.cache"))


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
    logger.debug(f"Selected a new bundle option: {selected_bundle}")
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\nSelected {selected_bundle}\n")
        log_text.see(tk.END)
    
    VariableManager().saveVariableInfo("selected_bundle", selected_bundle)

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
    selected_container = which_one[y.get()]
    logger.debug(f"Selected a new container option: {selected_container}")
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\nSelected {selected_container}\n")
        log_text.see(tk.END)

    VariableManager().saveVariableInfo("selected_container", selected_container)

    return selected_container