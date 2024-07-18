from . import (
    tk, filedialog
)
from .get_bin_path import BinaryPaths
from .managed_process import managedProcess

from .logger_config_class import YemenIPCCLogger

logger = YemenIPCCLogger().logger
bin_paths = BinaryPaths().getPaths()

ideviceinstaller = bin_paths["ideviceinstaller"]
args = bin_paths["args"]

    
def injectFromFile(log_text) -> None:
    """
    Injects the selected ipcc file manually
    """

    filepath = filedialog.askopenfilename(initialdir="./",
                                         title="Select IPCC file",
                                          filetypes=(("IPCC Files", "*.ipcc"),("All Files", "*.*"))
                                          )
    
    if filepath:
        with managedProcess([ideviceinstaller, "install", filepath], **args) as inject_from_file_process:
            # pass
            stdout = inject_from_file_process.communicate()[0]
            stderr = inject_from_file_process.communicate()[1]
            result = stdout + stderr
                        # Colors the logs
            if "SUCCESS: " in result:
                color = "green"
            elif "Install: Complete" in result:
                color = "green"
            elif "ERROR: " in result:
                logger.error(f"An error happened in the removal, error: {result}")
                color = "red"
            elif "No device found":
                color = "red"
            else:
                color = "grey"

            log_text.tag_configure(color, foreground=color)
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, f"\n{result}\n", color)
            log_text.see(tk.END)