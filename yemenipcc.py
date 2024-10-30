import os
import platform
import signal
import asyncio
from pathlib import Path


from resources.core.main_window import App
from resources.database.db import DataBase
from resources.utils.logger_config_class import YemenIPCCLogger

from resources.handles.exit_handle import handleExit
from resources.misc.temp_uuid import createNewUUID
from resources.misc.win_console_allocation import winLogsInit
from resources.utils.get_app_dir import getAppDirectory
from resources.utils.set_exec_perm import setExecutePermission
from resources.utils.set_font import setFont
from resources.utils.get_os_lang import isItArabic

from resources.utils.get_system import system


async def main():
    DataBase.addOnce(["arabic"], [isItArabic()], "app")

    DataBase.addOnce(
        ["dark", "medium", "light", "text"],
        ["#030b2c", "#0a1750", "#3b56bc", "white"],
        table="colors",
    )

    DataBase.addOnce(["enable", "custom_url"], [True, ""], table="discord")

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
    logger.debug(f"Current directory: {Path.cwd()}")

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
    if (
            str(app_directory).endswith("/Content/MacOS")
            # the reason why I'm also including the __init__.py is to really make sure we are in the right directory
            # if a person has a folder called "resources" in the same where the shell ran, this would cause errors
            or not (Path.cwd() / "resources" / "__init__.py").exists()
    ):
        os.chdir(app_directory)
        logger.debug(f"Switched directory to {app_directory}")

    setExecutePermission()

    # Executes the main program
    await App().start()


if __name__ == "__main__":
    asyncio.run(main())
