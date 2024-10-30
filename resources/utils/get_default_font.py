import subprocess
from functools import cache


from utils.managed_process import managedProcess

from utils.get_system import system


@cache
def getDefaultFont() -> str:
    """
    Gets the default font for the running system
    """

    if system == "Windows":
        return "Segoe UI"
    elif system == "Darwin":  # macOS
        return "SF Pro"
    elif system == "Linux":
        return getLinuxDefaultFont()
    else:
        return "Sans"  # Default to a generic font if OS is not recognized


@cache
def getLinuxDefaultFont() -> str:
    """
    Parsers the linux processes to determine which DE is it, and return it's suitable font name
    """
    # Define processes commonly associated with each DE
    de_processes = {
        "gnome": ["gnome-shell", "gnome-session"],
        "kde": ["plasmashell", "kwin_x11"],
        "xfce": ["xfce4-session"],
        "lxde": ["lxsession"],
        "mate": ["mate-session"],
        "cinnamon": ["cinnamon-session"],
        "unity": ["unity-panel-service"],
        "deepin": ["dde-session-daemon"],
        "pantheon": ["gala", "wingpanel"],
        "budgie": ["budgie-wm"],
        "i3": ["i3"],
        "sway": ["sway"],
        "enlightenment": ["enlightenment"],
    }

    try:
        # Get the list of running processes
        with managedProcess(
            ["ps", "-e", "-o", "comm="], stdout=subprocess.PIPE
        ) as process:
            stdout = process.stdout
            running_processes = stdout.decode().splitlines()

        # Check for known processes
        for de, processes in de_processes.items():
            for p in processes:
                if p in running_processes:
                    if de == "gnome":
                        return "Cantarell"
                    elif de == "kde":
                        return "Oxygen"
                    elif de == "xfce":
                        return "DejaVu Sans"
                    elif de == "lxde":
                        return "Liberation Sans"
                    elif de == "mate":
                        return "Ubuntu"
                    elif de == "cinnamon":
                        return "Noto Sans"
                    elif de == "unity":
                        return "Ubuntu"
                    elif de == "deepin":
                        return "Noto Sans"
                    elif de == "pantheon":
                        return "Open Sans"
                    elif de == "budgie":
                        return "Noto Sans"
                    elif de == "i3":
                        return "DejaVu Sans"
                    elif de == "sway":
                        return "DejaVu Sans"
                    elif de == "enlightenment":
                        return "Noto Sans"
        return "Sans"  # Default to a generic font if DE is not recognized
    except Exception as e:
        print("Error:", e)
        return "Sans"  # Default to a generic font in case of any error
