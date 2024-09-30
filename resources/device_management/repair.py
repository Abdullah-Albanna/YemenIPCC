import tkinter as tk
from tkinter import messagebox
import subprocess
from time import sleep


from ..utils.logger_config_class import YemenIPCCLogger
from ..utils.get_bin_path import BinaryPaths
from ..database.db import DataBase

from ..thread_management.thread_starter import startThread
from ..utils.managed_process import managedProcess
from ..arabic_tk.bidid import renderBiDiText
from ..utils.errors_stack import getStack
from ..utils.get_os_lang import isItArabic

from ..utils.get_system import system


logger = YemenIPCCLogger().logger
bin_paths = BinaryPaths().getPaths()

idevicepair = bin_paths["idevicepair"]
kwargs = bin_paths["kwargs"]

arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]


def validateDevice() -> str | bool:
    """
    Validate the device connection.

    Returns:
        str | bool: A string indicating the validation status ("passcode", "accept", "success") or a boolean (True or False).
    """
    try:

        with managedProcess([idevicepair, "validate"], **kwargs) as validate:
            stdout = validate.communicate()[0]
            stderr = validate.communicate()[1]
            result = stdout + stderr
        if "Please enter the passcode on the device and retry" in result:
            return "passcode"
        elif "Please accept the trust dialog on the screen of device" in result:
            return "accept"
        elif "Validated pairing with device" in result:
            return True
        elif "Device validation failed: unhandled error code -5" in result:
            return False
        elif "Please enter the passcode on the device and retry" in result:
            return False
        elif "said that the user denied the trust dialog." in result:
            return "denied"

    except subprocess.CalledProcessError as e:
        error_message: str = e.stderr.strip()
        logger.error(f"{error_message}, stack: {getStack()}")


def repairiPhone(log_text) -> None:
    """
    Re-pair the iPhone connection.

    Args:
        log_text: The text widget to display log messages.
    """
    # Ask for confirmation before proceeding with iPhone re-pair
    if not messagebox.askyesno(
        "Confirm",
        (
            renderBiDiText("هل انت متاكد من إعاده الاقتران")
            if arabic
            else f"Are you sure that you want to re-pair connected iPhone from your {system}?"
        ),
    ):
        return

    # Unpair the iPhone
    with managedProcess([idevicepair, "unpair"], **kwargs) as unpair_process:
        stdout = unpair_process.communicate()[0]
        stderr = unpair_process.communicate()[1]
        result = stdout + stderr
    
    # Place holder
    ar_result = ""

    # To avoid it logger "No Device found." twice
    if "No device found, is it plugged in?" in result or "No device found." in result:
        startThread(lambda: pairAndCheck(log_text), "pairAndCheck")
        return

    if "SUCCESS: " in result:

        color = "green"
        ar_result = renderBiDiText("تم إلغاء الاقتران بالجهاز بنجاح")
        logger.debug("unpaired with the device successfully")

    elif "ERROR: " in result:

        if "Please accept the trust dialog on the screen of device" not in result:
            if "is not paired with this host" not in result:
                logger.warning(
                    f"An error occurred in the repairiPhone(), error result: {result}"
                )

        color = "red"

    elif "No device found.":

        color = "red"
        ar_result = renderBiDiText("لم يتم العثور على جهاز متصل")

    elif "Please accept the trust dialog on the screen of device" in result:

        color = "blue"
        ar_result = renderBiDiText("يرجى قبول الثقة الذي يظهر على شاشة الجهاز")

    else:
        color = "grey"

    # Insert unpair log output into the log text widget if the device is plugged
    if arabic:
        if ar_result:
            if ar_result is not None:
                log_result = ar_result
            else:
                log_result = result
        else:
            log_result = result
    else:
        log_result = result
        
    log_text.tag_configure(color, foreground=color)
    log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
    log_text.insert(tk.END, f"\n{log_result}\n", color)
    log_text.see(tk.END)

    # Start a thread to pair the iPhone again and check the validation
    startThread(lambda: pairAndCheck(log_text), "pairAndCheck")


def pairAndCheck(log_text) -> None:
    """
    Pair the iPhone and check validation.

    args:
        log_text: The text widget to display log messages.
    """
    # Keep trying to pair the iPhone and check validation
    while True:
        # Pair the iPhone
        with managedProcess([idevicepair, "pair"], **kwargs) as pair:
            stdout = pair.communicate()[0]
            stderr = pair.communicate()[1]
            result = stdout + stderr
            
        # Place holder
        ar_result = ""

        if "SUCCESS: " in result:

            color = "green"
            ar_result = renderBiDiText("تم الاقتران بالجهاز بنجاح")
            logger.debug("Paired with the device successfully")

        elif "ERROR: " in result:

            if "Please enter the passcode on the device" not in result:
                if (
                    "Please accept the trust dialog on the screen of device" not in result
                ):
                    color = "red"
                    logger.error(
                        f"An error occurred in the pairAndCheck(), error result: {result}, stack: {getStack()}"
                    )
            color = "yellow"

        elif "No device found.":

            color = "yellow"
            ar_result = renderBiDiText("لم يتم العثور على جهاز متصل")

        else:
            color = "grey"

        # Insert pair log output into the log text widget
        if arabic:
            if ar_result:
                if ar_result is not None:
                    log_result = ar_result
                else:
                    log_result = result
            else:
                log_result = result
        else:
            log_result = result
        log_text.tag_configure(color, foreground=color)
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\n{log_result}\n", color)
        log_text.see(tk.END)

        # If pairing is successful, break the loop
        if (
            "SUCCESS: Paired with device" in result
        ):
            break

        # If device is not plugged, or the binary has bugs, it breaks out of the loop
        if (
            "No device found, is it plugged in?" in result
        ):
            break

        elif "No device found." in result:
            break

        elif "symbol lookup error" in result:
            logger.critical(
                f"An error occurred, possibly library error, error: {result}"
            )
            break
        elif "lockdownd_pair_cu" in result:
            logger.critical(
                f"An error occurred, possibly library error, error: {result}"
            )
            break

        # Validate the device and take action accordingly
        validation = validateDevice()
        if validation == "passcode":
            messagebox.showinfo(
                "Trust",
                (
                    renderBiDiText(
                        f"{system} اكتب كلمة المرور الخاصة بك في هاتفك لتثق بجهاز"
                    )
                    if arabic
                    else f"type your password in your phone to trust your {system} machine"
                ),
            )
        elif validation == "accept":
            messagebox.showinfo(
                "Accept",
                (
                    renderBiDiText(
                        f"{system} اقبل مربع حوار الثقة الذي يظهر على الشاشة لتثق في جهاز"
                    )
                    if arabic
                    else f"accept the trust dialog on the screen to trust your {system} machine"
                ),
            )
        elif validation == "denied":
            messagebox.showerror(
                "Error",
                (
                    renderBiDiText(
                        "لقد رفضت الطلب، يرجى إعادة توصيل الجهاز والمحاولة مرة أخرى!"
                    )
                    if arabic
                    else "You denied the request, please reconnect the usb and try again!"
                ),
            )
            break
        sleep(1)
