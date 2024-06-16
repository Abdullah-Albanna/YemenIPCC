from .projectimports import os
from .logging_config import setupLogging
import logging

def setExecutePermission(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Check if file is executable
            if not os.access(file_path, os.X_OK):
                # Set execute permission
                logging.info(f"set_exec_perm.py - {file_path} does not have execute permission, giving it..")
                os.chmod(file_path, 0o755)