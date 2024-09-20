import os
import glob
from loguru import logger

from ..utils.get_app_dir import getAppDirectory

from .get_system import system


def setPermission(directory, permission) -> None:
    """
    Sets the proper execution permission for each file in the passed directory
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Check if file is executable
            if not os.access(file_path, os.X_OK):
                # Set execute permission
                logger.debug(
                    f"{file_path} does not have execute permission, giving it.."
                )
                os.chmod(file_path, permission)


def setExecutePermission():
    # It just automates the process, to make it easier for noobs
    pattern = os.path.join(
        getAppDirectory(), "resources", "*_binary"
    )  # This just takes the binary folders
    matching_folders = glob.glob(pattern)  # And this applies the wildcard

    for folder_path in matching_folders:
        if "windows_binary" not in folder_path:  # not necessary for windows
            if (
                "mac_binary" in folder_path and system != "Darwin"
            ):  #  If it detects the mac binary and it is not a mac machine, skip
                continue
            elif "linux_binary" in folder_path and system != "Linux":  # Same
                continue
            # Sets the permission
            setPermission(folder_path, 0o755)
