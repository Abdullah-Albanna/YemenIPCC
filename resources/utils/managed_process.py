import subprocess
from contextlib import contextmanager

from .logger_config_class import YemenIPCCLogger
from ..database.dict_control import DictControl

from .errors_stack import getStack

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
        error_str = str(e)

        if DictControl().shouldRun(error_str):
            logger.error(f"File not found error: {e}\nStack trace:\n\n{getStack()}")
            yield None

        else:
            yield None

    except Exception as e:
        error_str = str(e)

        if DictControl().shouldRun(error_str):
            logger.error(f"An error occurred: {e}\nStack trace:\n\n{getStack()}")
            yield None

        else:
            yield None
    finally:
        if process is not None:
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
            process.terminate()
            process.wait()
