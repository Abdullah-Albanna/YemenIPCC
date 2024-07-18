import subprocess
from contextlib import contextmanager

from .logger_config_class import YemenIPCCLogger

logger = YemenIPCCLogger().logger

@contextmanager
def managedProcess(*args, **kwargs):
    """
    This is a managed subprocess session

    it runs the process, once done, KILL IT, so it won't keep running all the time and outside of the program
    """
    process = subprocess.Popen(*args, **kwargs)
    try:
        yield process
    except Exception as e:
        logger.error(f"An error occurred in the managedProcess, error: {e}")
    finally:
        process.terminate()
        process.wait()