import socket

from database.dict_control import DictControl
from utils.logger_config_class import YemenIPCCLogger

logger = YemenIPCCLogger().logger


def checkInternetConnection() -> bool:
    """
    Check internet connection by creating a socket connection to a well-known IP address.

    Returns:
        bool: True if internet connection is available, False otherwise.
    """
    port = 53
    socket_timeout = 3

    try:
        with socket.create_connection(("1.1.1.1", port), timeout=socket_timeout):
            DictControl().runAgain("logged_os_err_warn")
            DictControl().runAgain("logged_no_internet_warn")

            return True

    except OSError as os_error:
        if DictControl().shouldRun("logged_os_err_warn"):
            logger.warning(
                f"Something went wrong in the checking for internet connectivity, error: {os_error}"
            )

    if DictControl().shouldRun("logged_no_internet_warn"):
        logger.warning("There is no internet")

    return False
