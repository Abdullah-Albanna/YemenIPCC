import requests
import re


from ..utils.logger_config_class import YemenIPCCLogger
from ..database.dict_control import DictControl
from ..config.secrets import Env

from ..utils.errors_stack import getStack

logger = YemenIPCCLogger().logger


def getVersionValidation(current_version) -> bool | None:
    """
    Returns a bool to whether the current running version is supported or not
    """

    url = f"https://raw.githubusercontent.com/{Env().repo}/app-source/versions.txt"
    try:
        response = requests.get(url)

        # If the request is a success
        if response.status_code == 200:
            valid_version = {}
            text = response.text  # Get the text of the raw file
            lines = text.strip().split("\n")  # Split it into lines
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)  # Split at the first ':'
                    valid_version[key.strip()] = value.strip()  # Puts it in a dict

            valid_str = valid_version.get(
                current_version
            )  # Get the status of this version
            if valid_str == "valid":
                return True
            elif valid_str == "invalid":
                return False
            else:
                return True

        else:
            logger.error(
                f"Failed to fetch URL: {response.status_code} - {response.reason}, stack: {getStack()}"
            )

    except requests.exceptions.RequestException as e:
        if DictControl().shouldRun("Failed to resolve github"):
            if not re.search(
                r"Temporary failure in name resolution|Failed to resolve", str(e)
            ):
                logger.warning(f"Error fetching URL: {e}")
