from . import (
    os, 
    logger
    )

def setExecutePermission(directory) -> None:
    """
    Sets the proper execution permission for each file in the passed directory
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Check if file is executable
            if not os.access(file_path, os.X_OK):
                # Set execute permission
                logger.debug(f"{file_path} does not have execute permission, giving it..")
                os.chmod(file_path, 0o755)