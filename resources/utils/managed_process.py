import subprocess
from typing import Generator, Optional
from pathlib import Path

from contextlib import contextmanager
from pprint import pformat

from utils.logger_config_class import YemenIPCCLogger
from utils.error_codes import ErrorCodes
from database.dict_control import DictControl
from utils.messageboxes import MessageBox

from utils.errors_stack import getStack

from utils.get_system import system

logger = YemenIPCCLogger().logger


class ProcessOutput:
    """Class to hold the output of a subprocess."""

    def __init__(self, stdout: str, stderr: str):
        self.stdout = str(stdout)
        self.stderr = str(stderr)


def printProcessInfo(args, kwargs):

    file_path = Path(args[0][0])

    # TODO: Do something to fix it or print the path and envs and stuff
    logger.error("A missing file is detected, or couldn't find it\n\n"
                 f"The stack: {getStack()}\n"
                 "the process info:\n\n"
                 f"args: {pformat(args)}\n\n"
                 f"kwargs: {pformat(kwargs)}\n\n"
                 f"The binary path is {file_path}, exists: {file_path.exists()}")


@contextmanager
def managedProcess(
    *args, **kwargs
) -> Generator[Optional[ProcessOutput], None, None]:
    """
    This is a managed subprocess session.

    It runs the process, and once done, it ensures that the process is terminated
    to prevent it from running outside the program.
    """

    process = None
    try:
        process: subprocess.CompletedProcess = subprocess.run(*args, **kwargs)

        output = ProcessOutput(stdout=process.stdout, stderr=process.stderr)

        yield output

    except FileNotFoundError as e:
        if system == "Windows":
            if e.winerror == 2:
                printProcessInfo(args, kwargs)
                return

        e = str(e)

        if DictControl().shouldRun("Subprocess_File_Not_Found"):
            printProcessInfo(args, kwargs)

            MessageBox().showerror(
                "Critical Error",
                f"{ErrorCodes.FILE_NOT_FOUND.value} Something very bad happened. \n\nPlease contact me",
            )

        yield None

    except subprocess.CalledProcessError as cpe:
        cpe = str(cpe)
        if DictControl().shouldRun("Subprocess_CalledProcess_ERROR"):
            logger.error(f"An error occurred: {cpe}\nStack trace:\n\n{getStack()}")

            MessageBox().showerror(
                "Critical Error",
                f"{ErrorCodes.PROCESS_ERROR.value} An error occurred, you might need to try again",
            )

        yield None

    except Exception as e:
        e = str(e)

        if DictControl().shouldRun("Subprocess_Unknown_ERROR"):
            logger.error(f"An error occurred: {e}\nStack trace:\n\n{getStack()}")

            MessageBox().showerror(
                "Critical Error",
                f"{ErrorCodes.UNKNOWN_ERROR.value} Something very bad happened. \n\nPlease contact me",
            )

        yield None

    finally:

        if hasattr(process, "communicate"):
            if process is not None:
                if process.stdout:
                    process.stdout.close()
                if process.stderr:
                    process.stderr.close()
                process.terminate()
                process.wait()
