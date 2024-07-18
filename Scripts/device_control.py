from . import (
    tk,
    logger
)
from .managed_process import managedProcess
from .get_bin_path import BinaryPaths

bin_paths = BinaryPaths().getPaths()

idevicediagnostics = bin_paths["idevicediagnostics"]
args = bin_paths["args"]

def deviceControl(action: str, log_text) -> None:
    """
    Controls the iPhone to restart or shutdown or even sleep
    """
    with managedProcess([idevicediagnostics, action], **args) as device_process:
        stdout = device_process.communicate()[0]
        stderr = device_process.communicate()[1]
        result = stderr + stdout
        
        if "ERROR" in result:
            color = "red"
            logger.warning(result)
        elif "No device found." in result:
            logger.debug(result)
            color = "yellow"
        else:
            logger.debug(result)
        
        log_text.tag_configure(color, foreground=color)
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\n{result}", color)
        log_text.see(tk.END)