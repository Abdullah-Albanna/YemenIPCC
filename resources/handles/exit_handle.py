import sys
import os
from time import sleep


from ..database.db import DataBase
from ..thread_management.thread_starter import killThreads
from ..thread_management.thread_terminator_var import terminate


def handleExit(signum=None, frame=None, status_code = 0):
    """
    An extra step to close the app better
    """
    # if "-d" in sys.argv:
    print("\033[33mExiting gracefully...\033[0m")

    # Blocks any output and input after the exiting message
    with open(os.devnull, "w") as devnull:
        sys.stdout = devnull
        sys.stderr = devnull
        sys.stdin = devnull
    DataBase.add(["iPhone_version"], [""], "iphone")
    DataBase.add(["iPhone_model"], [""], "iphone")
    DataBase.add(["iPhone_model_alt"], [""], "iphone")
    sleep(0.7)
    terminate.set()
    killThreads()
    sys.exit(status_code)
