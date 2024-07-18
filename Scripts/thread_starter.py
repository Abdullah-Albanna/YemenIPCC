from . import (
    thread
)
from .logger_config_class import YemenIPCCLogger

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
            thread_name.kill(yielding=False, timeout=3)

def startThread(target, name, daemon=None, *args) -> None:
    """
    It just starts the thread with logging
    """
    try:
        thread_name = thread.Thread(target=target, args=args, daemon=True if daemon is None else False, name=name)
        thread_name.start()
        registerThread(thread_name)
        logger.debug(f"Ran the {name} thread")

    except RuntimeError as e:
        logger.error(f"An error occurred while running the {name} thread, error: {e}")