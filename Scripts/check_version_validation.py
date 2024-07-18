from . import (
    requests
)
from .logger_config_class import YemenIPCCLogger

logger = YemenIPCCLogger().logger

def getVersionValidation(current_version) -> bool:
    """
    Returns a bool to whether the current running version is supported or not
    """

    url = 'https://raw.githubusercontent.com/Abdullah-Albanna/YemenIPCC/app-source/versions.txt'

    try:
        response = requests.get(url)
        
        # If the requiest is a success
        if response.status_code == 200:
            valid_version = {}
            text = response.text # Get the text of the raw file
            lines = text.strip().split('\n') # Split it into lines
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)  # Split at the first ':'
                    valid_version[key.strip()] = value.strip() # Puts it in a dict

            valid_str = valid_version.get(current_version) # Get the status of this version
            if valid_str == "valid":
                return True
            else:
                return False
        
        else:
            logger.error(f"Failed to fetch URL: {response.status_code} - {response.reason}")

    except requests.exceptions.RequestException as e:
        if not "Failed to resolve 'raw.githubusercontent.com'" in e:
            logger.warning(f"Error fetching URL: {e}")