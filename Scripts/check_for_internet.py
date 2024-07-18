from . import(
    socket, 
    logger
)
from Scripts.dict_control import DictControl

def checkInternetConnection() -> bool:

    """
    Check internet connection by creating a socket connection to a well-known IP address.

    Returns:
        bool: True if internet connection is available, False otherwise.
    """
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=5)
        DictControl().runAgain('logged_oser_warn')
        DictControl().runAgain('logged_noint_warn')

        return True
    except OSError as oser:
        if DictControl().shouldRun('logged_oser_warn'):
            logger.warning(f"Something went wrong in the checking for internet conectivity, error: {oser}")

    if DictControl().shouldRun('logged_noint_warn'):
        logger.warning("There is no internet")

    return False