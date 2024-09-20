import os
import subprocess
from typing import Dict


from .get_system import system


class BinaryPaths:
    def __init__(self):
        self.ideviceinfo = None
        self.ideviceinstaller = None
        self.idevicediagnostics = None
        self.idevicesyslog = None
        self.idevicepair = None
        self.idevice_id = None
        self.env = None
        self.kwargs = None

        self.setupPaths()

    def setupPaths(self) -> None:
        # What these three do is specifing the executeable binary for each system so the user do not have to install anything
        if system == "Mac":

            # This sets the library looking path to the project's library, again, to make the user not install anything
            os.environ["DYLD_LIBRARY_PATH"] = (
                "./resources/bin/mac_binary/lib:$DYLD_LIBRARY_PATH"
            )

            # Copies the path so it could be passed to the subprocesses
            self.env = os.environ.copy()

            self.idevice_id: str = "./resources/bin/mac_binary/idevice_id"
            self.idevicepair: str = "./resources/bin/mac_binary/idevicepair"
            self.ideviceinfo: str = "./resources/bin/mac_binary/ideviceinfo"
            self.ideviceinstaller: str = "./resources/bin/mac_binary/ideviceinstaller"
            self.idevicediagnostics: str = (
                "./resources/bin/mac_binary/idevicediagnostics"
            )
            self.idevicesyslog: str = "./resources/bin/mac_binary/idevicesyslog"

        if system == "Linux":

            # The same, but only change the env variable for linux
            os.environ["LD_LIBRARY_PATH"] = (
                "./resources/bin/linux_binary/lib:$LD_LIBRARY_PATH"
            )
            self.env = os.environ.copy()

            self.idevice_id: str = "./resources/bin/linux_binary/idevice_id"
            self.idevicepair: str = "./resources/bin/linux_binary/idevicepair"
            self.ideviceinfo: str = "./resources/bin/linux_binary/ideviceinfo"
            self.ideviceinstaller: str = "./resources/bin/linux_binary/ideviceinstaller"
            self.idevicediagnostics: str = (
                "./resources/bin/linux_binary/idevicediagnostics"
            )
            self.idevicesyslog: str = "./resources/bin/linux_binary/idevicesyslog"

        elif system == "Windows":

            self.idevice_id: str = ".\\resources\\bin\\windows_binary\\idevice_id.exe"
            self.idevicepair: str = ".\\resources\\bin\\windows_binary\\idevicepair.exe"
            self.ideviceinfo: str = ".\\resources\\bin\\windows_binary\\ideviceinfo.exe"
            self.ideviceinstaller: str = (
                ".\\resources\\bin\\windows_binary\\ideviceinstaller.exe"
            )
            self.idevicediagnostics: str = (
                ".\\resources\\bin\\windows_binary\\idevicediagnostics.exe"
            )
            self.idevicesyslog: str = (
                ".\\resources\\bin\\windows_binary\\idevicesyslog.exe"
            )
            self.env = os.environ.copy()

            # Adds the CREATE_NO_WINDOW for windows (hides the terminal)
            self.kwargs = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "env": self.env,
                "creationflags": subprocess.CREATE_NO_WINDOW,
            }

        # Don't for others, not needed for them and not even avaliable
        if system != "Windows":

            self.kwargs = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "env": self.env,
            }

    def getPaths(self) -> Dict[str, any]:
        """
        Returns the executable binary paths, required subprocess kwargs, the env for the binary to look for the library
        """
        return {
            "ideviceinfo": self.ideviceinfo,
            "ideviceinstaller": self.ideviceinstaller,
            "idevicediagnostics": self.idevicediagnostics,
            "idevicesyslog": self.idevicesyslog,
            "idevicepair": self.idevicepair,
            "idevice_id": self.idevice_id,
            "env": self.env,
            "kwargs": self.kwargs,
        }
