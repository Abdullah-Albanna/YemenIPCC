import os
import platform
import signal

from resources.config.version import CURRENT_VERSION
from resources.core.main_window import App
from resources.database.db import DataBase
from resources.handles.exit_handle import handleExit
from resources.misc.temp_uuid import createNewUUID
from resources.misc.win_console_allocation import winLogsInit
from resources.utils.get_app_dir import getAppDirectory
from resources.utils.get_system import system
from resources.utils.logger_config_class import YemenIPCCLogger
from resources.utils.set_exec_perm import setExecutePermission
from resources.utils.set_font import setFont
from resources.utils.get_os_lang import isItArabic

if __name__ == "__main__":
    DataBase.addOnce(["arabic"], [isItArabic()], "app")

    DataBase.addOnce(
        ["dark", "medium", "light", "text"],
        ["#030b2c", "#0a1750", "#3b56bc", "white"],
        table="colors",
    )

    DataBase.addOnce(["enable", "custom_url"], [True, ""], table="discord")

    arabic = DataBase.get(["arabic"], [isItArabic()], table="app")[0]

    # Resets the bundle to default on each start
    DataBase.add(
        ["selected_bundle", "selected_container"],
        ["CellularSouthLTE", "default.bundle"],
        table="bundle",
    )
    DataBase.add(["running", "validate"], [False, True], table="injection")

    setFont()

    # # If the system is Windows, this will allocate a new console for logging if -d is passed.
    winLogsInit()

    # Register the signal handlers
    signal.signal(signal.SIGINT, handleExit)
    signal.signal(signal.SIGTERM, handleExit)

    # Sets up the logger
    logger = YemenIPCCLogger().logger
    YemenIPCCLogger().run()

    # Creates a new UUID for each run if it is not already created, this is used for the activity updates
    createNewUUID()

    logger.debug(f"OS: {platform.platform()}")

    # This is necessary, it changes to the app directory so the app would run normally if you run the script from
    # another directory
    app_directory = getAppDirectory()
    logger.debug(f"App directory is: {app_directory}")
    logger.debug(f"Current directory: {os.getcwd()}")

    # Logs the distro
    if system == "Linux":
        logger.debug(
            f"Linux Distribution: {platform.freedesktop_os_release().get('PRETTY_NAME')}"
        )
        logger.debug(
            f"Linux Version: {platform.freedesktop_os_release().get('VERSION')}"
        )

    # If the current running directory is in the macOS bundle app, or there is no folder called "resources" in the
    # current directory then change the current directory to the executed script directory
    if app_directory.endswith("/Content/MacOS") or not os.path.exists(
        os.path.join(os.getcwd(), "resources")
    ):
        os.chdir(app_directory)
        logger.debug(f"Switched directory to {app_directory}")

    # Writes the app version in a __version__ file
    with open(os.path.join(".", "__version__"), "w") as file:
        file.write(CURRENT_VERSION)

    setExecutePermission()

    # Executes the main program
    App()
