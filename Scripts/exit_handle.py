from . import (
    sys, os, 
    sleep
)
from .thread_terminator_var import terminate
from .thread_starter import killThreads

def handleExit(signum=None, frame=None):
    """
    An extra step to close the app better
    """
    if "-d" in sys.argv:
        print("\033[33mExiting gracefully...\033[0m")

    # Blocks any output after the exiting message
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        sys.stderr = devnull
    sleep(1.3)
    terminate.set()
    killThreads()
    sys.exit(0)