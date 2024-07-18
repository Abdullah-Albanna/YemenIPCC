from . import (
    tk, ctypes, 
    sleep
    )
from .logger_config_class import YemenIPCCLogger
# from .variables_manager import VariableManager
# from .splash_screen import terminatp

logger = YemenIPCCLogger().logger
from .get_system import system


def setDpiAwareness() -> None:
    """
    Sets up the dpi for windows
    """

    if system == "Windows":
        try:
            # Try to set the DPI awareness for the application (Windows 8.1 and later)
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE = 1
        except Exception as e:
            try:
                # For older versions of Windows
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception as e:
                logger.error(f"Could not set DPI awareness: {e}")
    else:
        pass


def centerWindow(window: tk.Tk) -> None:

    """
    Center the window on the screen.

    Args:
        window (tk.Tk): The tkinter window to center.
    """
    # Update the window to get its actual size
    window.update_idletasks()  

    # Get window dimensions
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight() 

    # Calculate window position
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2  - 50 # For task bar
    
    # Set window position
    window.geometry(f"+{x}+{y}")

    setDpiAwareness()

def showWindow(window: tk.Tk) -> None:

    """
    Show the window.

    Args:
        window (tk.Tk): The tkinter window to show.
    """
    window.deiconify()

def initialize(window: tk.Tk) -> None:
    
    """
    Initialize the window by centering it and showing it after a delay.

    Args:
        window (tk.Tk): The tkinter window to initialize.
    """
    centerWindow(window)
    
    # Delay the appearance of the window to ensure proper resizing and centering
    window.after(100, lambda: showWindow(window))
