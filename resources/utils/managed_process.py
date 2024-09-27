import subprocess
import sys
from tkinter import messagebox
from contextlib import contextmanager


from .logger_config_class import YemenIPCCLogger
from .error_codes import ErrorCodes
from ..database.dict_control import DictControl

from .errors_stack import getStack
from ..handles.exit_handle import handleExit

logger = YemenIPCCLogger().logger


@contextmanager
def managedProcess(*args, **kwargs):
    """
    This is a managed subprocess session.

    It runs the process, and once done, it ensures that the process is terminated
    to prevent it from running outside the program.
    """

    process = None
    try:
        process = subprocess.Popen(*args, **kwargs)
        yield process

    except FileNotFoundError as e:
        e = str(e)

        if DictControl().shouldRun("Subprocess_File_Not_Found"):
            logger.critical(f"File not found error: {e}\nStack trace:\n\n{getStack()}")

            messagebox.showerror(
                "Critical Error",
                f"{ErrorCodes.FILE_NOT_FOUND.value} Something very bad happened. \n\nPlease contact me",
            )

        yield None

    except Exception as e:
        e = str(e)

        if DictControl().shouldRun("Subprocess_Unknown_ERROR"):
            logger.error(f"An error occurred: {e}\nStack trace:\n\n{getStack()}")

            messagebox.showerror(
                "Critical Error",
                f"{ErrorCodes.UNKNOWN_ERROR.value} Something very bad happened. \n\nPlease contact me",
            )

        yield None

    finally:
        if process is not None:
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
            process.terminate()
            process.wait()
