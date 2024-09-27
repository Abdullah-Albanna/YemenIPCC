import os
import subprocess
from typing import Dict


from .get_app_dir import getAppDirectory
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

        self.base_dir = os.path.join(getAppDirectory(), "resources", "bin")

        self.setupPaths()

    def setupPaths(self) -> None:
        # What these three do is specifing the executeable binary for each system so the user do not have to install anything
        if system == "Mac":
            bin_base_dir = os.path.join(self.base_dir, "mac_binary")
            lib_path_env = "DYLD_LIBRARY_PATH"

        elif system == "Linux":
            bin_base_dir = os.path.join(self.base_dir, "linux_binary")
            lib_path_env = "LD_LIBRARY_PATH"
        elif system == "Windows":
            bin_base_dir = os.path.join(self.base_dir, "windows_binary")

        if system in ["Mac", "Linux"]:
            os.environ[lib_path_env] = (
                f'{os.path.join(bin_base_dir, "lib")}:${lib_path_env}'
            )
            self.env = os.environ.copy()

        self.setupBinaryPaths(bin_base_dir)
        
        self.setupSubprocessOptions()

    def setupBinaryPaths(self, bin_base_dir):
        if system in ["Mac", "Linux"]:
            file_extension = ""
        elif system == "Windows":
            file_extension = ".exe"

        self.idevice_id = os.path.join(bin_base_dir, f"idevice_id{file_extension}")

        self.idevicediagnostics = os.path.join(
            bin_base_dir, f"idevicediagnostics{file_extension}"
        )

        self.ideviceinfo = os.path.join(bin_base_dir, f"ideviceinfo{file_extension}")

        self.ideviceinstaller = os.path.join(
            bin_base_dir, f"ideviceinstaller{file_extension}"
        )

        self.idevicepair = os.path.join(bin_base_dir, f"idevicepair{file_extension}")
        
        self.idevicesyslog = os.path.join(
            bin_base_dir, f"idevicesyslog{file_extension}"
        )

        # if system == "Mac":
        #     mac_base_dir = os.path.join(self.base_dir, "mac_binary")

        #     # This sets the library looking path to the project's library, again, to make the user not install anything
        #     os.environ["DYLD_LIBRARY_PATH"] = (
        #         f"{os.path.join(mac_base_dir, "lib")}:$DYLD_LIBRARY_PATH"
        #     )

        #     # Copies the path so it could be passed to the subprocesses
        #     self.env = os.environ.copy()

        #     self.idevice_id: str = os.path.join(mac_base_dir, "idevice_id")
        #     self.idevicepair: str = os.path.join(mac_base_dir, "idevicepair")
        #     self.ideviceinfo: str = os.path.join(mac_base_dir, "ideviceinfo")
        #     self.ideviceinstaller: str = os.path.join(mac_base_dir, "ideviceinstaller")
        #     self.idevicediagnostics: str = os.path.join(
        #         mac_base_dir, "idevicediagnostics"
        #     )
        #     self.idevicesyslog: str = os.path.join(mac_base_dir, "idevicesyslog")

        # if system == "Linux":
        #     linux_base_dir = os.path.join(self.base_dir, "linux_binary")

        #     # The same, but only change the env variable for linux
        #     os.environ["LD_LIBRARY_PATH"] = (
        #         f"{os.path.join(linux_base_dir, "lib")}:$LD_LIBRARY_PATH"
        #     )
        #     self.env = os.environ.copy()

        #     self.idevice_id: str = os.path.join(linux_base_dir, "idevice_id")
        #     self.idevicepair: str = os.path.join(linux_base_dir, "idevicepair")
        #     self.ideviceinfo: str = os.path.join(linux_base_dir, "ideviceinfo")
        #     self.ideviceinstaller: str = os.path.join(
        #         linux_base_dir, "ideviceinstaller"
        #     )
        #     self.idevicediagnostics: str = os.path.join(
        #         linux_base_dir, "idevicediagnostics"
        #     )
        #     self.idevicesyslog: str = os.path.join(linux_base_dir, "idevicesyslog")

        # elif system == "Windows":
        #     win_base_dir = os.path.join(self.base_dir, "windows_binary")

        #     self.idevice_id: str = os.path.join(win_base_dir, "idevice_id")
        #     self.idevicepair: str = os.path.join(win_base_dir, "idevicepair")
        #     self.ideviceinfo: str = os.path.join(win_base_dir, "ideviceinfo")
        #     self.ideviceinstaller: str = os.path.join(win_base_dir, "ideviceinstaller")

        #     self.idevicediagnostics: str = os.path.join(
        #         win_base_dir, "idevicediagnostics"
        #     )

        #     self.idevicesyslog: str = os.path.join(win_base_dir, "idevicesyslog")

        #     self.env = os.environ.copy()

        #     # Adds the CREATE_NO_WINDOW for windows (hides the terminal)
        #     self.kwargs = {
        #         "stdout": subprocess.PIPE,
        #         "stderr": subprocess.PIPE,
        #         "text": True,
        #         "env": self.env,
        #         "creationflags": subprocess.CREATE_NO_WINDOW,
        #     }

        # # Don't for others, not needed for them and not even avaliable
        # if system != "Windows":
        #     self.kwargs = {
        #         "stdout": subprocess.PIPE,
        #         "stderr": subprocess.PIPE,
        #         "text": True,
        #         "env": self.env,
        #     }
    def setupSubprocessOptions(self):
        self.kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "env": self.env,
        }
        
        if system == "Windows":
            self.kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW # type: ignore

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
