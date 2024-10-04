from threading import Thread
import ctypes


from utils.logger_config_class import YemenIPCCLogger

from utils.errors_stack import getStack

logger = YemenIPCCLogger().logger
thread_registry: list = []


def registerThread(thread):
    """
    Appends the thread to a list
    """
    thread_registry.append(thread)


def killThreads():
    """
    Kill any every registred thread.

    Used once the program exits
    """
    for thread_name in thread_registry:
        if thread_name is not None and thread_name.is_alive():
            # Taken directly from https://pypi.org/project/stop-thread
            i_error = ctypes.py_object(InterruptedError)

            # if user clicks stop before doing anything
            try:
                tid = ctypes.c_long(thread_name.ident)
            except Exception:
                # logger.warning("Cant convert ident to ctypes.c_long: %s", exc)
                return

            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, i_error)

            if res > 1:
                # we are in trouble
                # call it again with None to revert the effect
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)


def startThread(target, name, daemon=True, *args) -> None:
    """
    It just starts the thread with logging
    """
    try:
        thread_name = Thread(
            target=target,
            args=args,
            daemon=daemon,
            name=name,
        )
        thread_name.start()
        registerThread(thread_name)
        logger.debug(f"Ran the {name} thread")

    except RuntimeError as e:
        logger.error(
            f"An error occurred while running the {name} thread, error: {e}, \nStack error:\n\n {getStack()}"
        )

    except Exception as e:
        logger.error(
            f"An error occurred while running the {name} thread, error: {e}, \nStack error:\n\n {getStack()}"
        )
