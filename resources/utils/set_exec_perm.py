import os
from loguru import logger
from pathlib import Path

from ..utils.get_app_dir import getAppDirectory

from .get_system import system


def setPermission(directory, permission) -> None:
    """
    Sets the proper execution permission for each file in the passed directory
    """
    for root, dirs, files in Path.walk(directory):
        for file in files:
            # file_path = os.path.join(root, file)
            file_path = Path(root, file).resolve()
            # Check if file is executable
            if not os.access(file_path, os.X_OK):
                # Set execute permission
                logger.debug(
                    f"{file_path} does not have execute permission, giving it.."
                )
                os.chmod(file_path, permission)


def setExecutePermission():
    
    # It just automates the process, to make it easier for noobs
    paths = (getAppDirectory() / "resources" / "bin").glob("*_binary")  # This just takes the binary folders

    # matching_folders = glob.glob(pattern)  # And this applies the wildcard

    for path in paths:
        if "windows_binary" not in path.parts:  # not necessary for windows
            if (
                "mac_binary" in path.parts and system != "Darwin"
            ):  #  If it detects the mac binary and it is not a mac machine, skip
                continue
            elif "linux_binary" in path.parts and system != "Linux":  # Same
                continue
            
            # Sets the permission
            setPermission(path, 0o755)
