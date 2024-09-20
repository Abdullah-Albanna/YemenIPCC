import requests
import webbrowser
import re
from tkinter import messagebox

from ..database.db import DataBase
from ..config.secrets import Env
from ..utils.logger_config_class import YemenIPCCLogger

from .check_for_internet import checkInternetConnection
from ..arabic_tk.bidid import renderBiDiText
from ..utils.errors_stack import getStack
from ..utils.get_os_lang import isItArabic

from ..utils.get_system import system

arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]
logger = YemenIPCCLogger().logger


def checkForUpdate(current_version: str, max_lines: int = 30) -> bool | str:
    """
    Args:
        current_version (str): The current version of the app.
        max_lines (int): Maximum number of lines to display in the message.

    Returns:
        Union[bool, str]: True if an update is available and user chooses to update,
                          False if there is no update available or there's an error fetching updates,
                          "No Internet" if there's no internet connection,
                          "No Update" if there is no new updates.
    """
    if not checkInternetConnection():
        return "No Internet"

    repo_url = f"https://api.github.com/repos/{Env().repo}/releases"

    try:
        response = requests.get(repo_url)
        response.raise_for_status()
    except requests.RequestException as e:
        if re.search(r"rate limit exceeded|Max retries exceeded with url", str(e)):
            logger.warning(
                "Checking for update has been block due to rate limit, please try after an hour"
            )
            return "rate limit"
        else:
            logger.error(f"Error fetching update information, error stack: {getStack()}")
        return False

    releases_info = response.json()

    for release in releases_info:
        for asset in release["assets"]:
            if system in asset["name"]:
                latest_version = release["tag_name"]
                size = asset["size"]
                message = release["body"]

                if current_version >= latest_version:
                    logger.info("There is no update")
                    return "No Update"
                else:
                    logger.info(f"There is a new update, version: {latest_version}")

                # Calculate number of lines in the message
                lines = len(message.splitlines())

                # Crop the message if it exceeds max_length lines
                if lines > max_lines:
                    message = (
                            "\n".join(message.splitlines()[:max_lines])
                            + "... Click Yes to Read the Rest"
                    )

                size_mb = round(size / (1024 * 1024), 2)
                update_message = (
                    f"A new version ({latest_version}) is available!\n"
                    f"Do you want to update?\n\n"
                    f"Size: {size_mb} MB\n\n"
                    f"Message:\n{message}"
                )
                arabic_update_message = (
                    f"إصدار جديد ({latest_version}) متاح!\n"
                    f"هل تريد التحديث؟\n\n"
                    f"الحجم: {size_mb} ميجابايت\n\n"
                    f"الرسالة:\n{message}"
                )

                if not messagebox.askyesno(
                        "Update Available",
                        arabic_update_message if arabic else update_message,
                ):
                    logger.info("User declined the update")
                    return False

                download_url = release["html_url"]
                webbrowser.open_new_tab(download_url)
                logger.info("User accepted the update")
                return True

    return "No Update"


def checkForUpdateButton(current_version: str) -> None:
    """
    This is mainly for the tools -> check for update button.

    Args:
        current_version (str): The current version of the app.
    Returns:
        None
    """
    update_result = checkForUpdate(current_version)
    if update_result == "No Update":
        messagebox.showinfo(
            "Check for Update",
            (
                renderBiDiText("Yemen IPCC\n محدث الى اخر اصدار")
                if arabic
                else "Yemen IPCC is up-to-date"
            ),
        )
    elif update_result == "No Internet":
        messagebox.showerror(
            "Error",
            (
                renderBiDiText("يرجى الاتصال بالانترنت")
                if arabic
                else "Please connect to the internet first"
            ),
        )
    elif update_result == "rate limit":
        messagebox.showerror(
            "Error",
            (
                renderBiDiText("يرجى المحاوله بعد ساعه")
                if arabic
                else "Please try after an hour"
            ),
        )
