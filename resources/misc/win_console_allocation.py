import sys


from ..utils.get_system import system

if system == "Windows":
    import win32console # type: ignore


def allocateConsole() -> None:
    """
    Allocates a new console for logging.
    """
    try:
        # This releases the current termainl
        win32console.FreeConsole()
        # And this creates a new one
        win32console.AllocConsole()
        win32console.SetConsoleTitle("Yemen IPCC Logs")

        sys.stdout = open("CONOUT$", "w")
        sys.stderr = open("CONOUT$", "w")

    except Exception as e:
        # This just means there is already a console, so you can't just make a new one, mainly if running source code
        print(e)
        if "'AllocConsole', 'Access is denied.'" not in str(e):
            print(f"An error occurred with pywin32, error: {e}")


def winLogsInit() -> None:
    """
    Initiate the console
    """
    if system == "Windows":
        if "-d" in sys.argv:
            allocateConsole()
