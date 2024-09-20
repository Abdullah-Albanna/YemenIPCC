from .. import (
    new_iPhone_message,
    new_iPhones,
    arabic_new_iphone_message,
)

import subprocess
import os
import aiohttp
import asyncio
import textwrap
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar, Style
from tempfile import TemporaryDirectory
from threading import Event
from time import sleep
from typing import List


from ..utils.logger_config_class import YemenIPCCLogger
from ..utils.get_bin_path import BinaryPaths
from .device_manager import DeviceManager
from ..database.db import DataBase
from ..core.api import API

from ..thread_managment.thread_starter import startThread
from ..checkers.check_for_internet import checkInternetConnection
from ..handles.send_data import sendData
from ..utils.managed_process import managedProcess
from ..utils.set_font import getFont
from ..utils.fix_ssl import fixSSL
from ..arabic_tk.bidid import renderBiDiText
from ..utils.errors_stack import getStack
from ..utils.get_os_lang import isItArabic

from ..thread_managment.thread_terminator_var import terminate

arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]
medium_color, light_color, text_color = DataBase.get(
    ["medium", "light", "text"], ["#0a1750", "#3b56bc", "white"], "colors"
)

logger = YemenIPCCLogger().logger
bin_paths = BinaryPaths().getPaths()

ideviceinfo = bin_paths["ideviceinfo"]
ideviceinstaller = bin_paths["ideviceinstaller"]
idevicediagnostics = bin_paths["idevicediagnostics"]
idevicesyslog = bin_paths["idevicesyslog"]
kwargs = bin_paths["kwargs"]


def readSysLog(log_queue, stop_event) -> None:
    """
    Reads the iPhone system logs to decide the result of the injection process
    """
    syslog_process = subprocess.Popen(
        [idevicesyslog], **kwargs, universal_newlines=True
    )
    try:
        while not stop_event.is_set():
            output = syslog_process.stdout.readline().strip()
            if output == "" and syslog_process.poll() is not None:
                break
            if output:
                log_queue.append(output)
    finally:
        syslog_process.stdout.close()
        syslog_process.stderr.close()
        syslog_process.terminate()
        syslog_process.wait()
        logger.debug("Stoppted readSysLog")


async def isFileDownloadable(url) -> bool:
    """
    Checks if the file exists or not by testing the downloading ability
    """
    # We well use aiohttp with async to get the fastest result
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.head(url, allow_redirects=True) as response:
                # Check if the request was successful
                if response.status != 200:
                    return False

                # Get the content type
                content_type = response.headers.get("Content-Type", "").lower()

                # Check if the content type is not HTML
                if "text/html" in content_type:
                    return False

                # Check for Content-Disposition header to see if it's an attachment
                content_disposition = response.headers.get(
                    "Content-Disposition", ""
                ).lower()
                if "attachment" in content_disposition:
                    return True

                # If there is no Content-Disposition header, infer from content type
                if content_type in ["application/octet-stream", "application/zip"]:
                    return True

                return False

        except aiohttp.ClientSSLError as e:
            logger.error(f"SSL Error: {e}, stack: {getStack()}")
            fixSSL()
            return False

        except aiohttp.ClientError as e:
            logger.error(
                f"An error occurred in the checking for the avalibility of a bundle: {e}, stack: {getStack()}"
            )
            return False

        finally:
            await session.close()


def replace_space(string):
    return string.replace(" ", "")


def replace_perc20(string):
    return string.replace("%20", " ").lower()


async def downloadFile(iPhone_model, iPhone_version, bundle, container):
    response = await API().genLink(iPhone_model, iPhone_version, bundle, container)

    return response


def removingAndInjectingIPCC(window: tk.Tk, log_text: tk.Text) -> None:
    """
    This is the main injection process.

    Args:
        window (tk.Tk): The tkinter window.
        log_text (tk.Text): The text widget for logger.
        selected_bundle (str): The selected bundle name.
        selected_container (str): The selected option name.
    """
    selected_bundle, selected_container = DataBase.get(
        ["selected_bundle", "selected_container"],
        ["CellularSouthLTE", "default.bundle"],
        "bundle",
    )
    # Sets the running variable to True so the button stop working, to avoid multi-clicking the button
    DataBase.add(["running"], [True], "injection")
    try:
        if not checkInternetConnection():
            messagebox.showerror(
                "No Internet",
                (
                    renderBiDiText("تاكد من الاتصال بالانترنت")
                    if arabic
                    else "Please make sure to connect to the internet first"
                ),
            )

            DataBase.add(["running"], [False], "injection")
            logger.debug("User tried to inject without internet")
            return
        # Get iPhone information
        product_version, product_type = DataBase.get(
            ["iPhone_version", "iPhone_model_alt"], ["unknown", "unknown"], "iphone"
        )

        is_new_iPhone = False

        # Create custom style for the progress bar. It looks better
        style = Style()
        style.theme_use("clam")

        # Configure colors and appearance for the custom style
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background=light_color,
            troughcolor="#FFFFFF",
            bordercolor=light_color,
            lightcolor=light_color,
            darkcolor=light_color,
            troughrelief="flat",
            troughborderwidth=9,
            borderwidth=0,  # No border
            relief="flat",  # Flat relief
        )

        # Create progress frame
        progress_frame = tk.Frame(window, bg=medium_color)  # Dark blue background
        progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Progress label
        progress_label = tk.Label(
            progress_frame,
            text=(
                renderBiDiText("التحقق من وجود الملف")
                if arabic
                else "Checking the existence of the file..."
            ),
            font=(getFont(), 14),
            bg=medium_color,
            fg=text_color,
        )  # Adjust font and colors
        progress_label.pack(pady=5)

        # Progress bar
        progress_bar = Progressbar(
            progress_frame,
            orient="horizontal",
            length=300,
            mode="indeterminate",
            style="Custom.Horizontal.TProgressbar",
        )  # Use custom style
        progress_bar.pack(pady=5)
        progress_bar.start(interval=50)  # Start the indeterminate progress bar

        # A small reuseable function to replace any whitespace with nothing and %20 with a dot, used for the url and a message

        # # Converts the .ipcc type option for the url
        # which_one_mappings: dict[str, str] = {
        #     "default.bundle": "Default%20Bundle",
        #     "unknown.bundle": "Unknown%20Bundle",
        # }

        # selected_container: str = which_one_mappings.get(
        #     selected_container, "Your not suppose to see this message ): "
        # )

        # URL for downloading IPCC
        # url = f"https://raw.githubusercontent.com/Abdullah-Albanna/YemenIPCC/master/{replace_space(product_type)}/iOS%20{product_version}/Using%20{selected_container}/{replace_space(product_type)}_iOS_{product_version}_{selected_bundle}.ipcc"
        download_process = asyncio.run(
            downloadFile(
                replace_space(product_type),
                product_version,
                selected_bundle,
                selected_container,
            )
        )

        window.update_idletasks()
        # downloadable = asyncio.run(isFileDownloadable(url))
        if download_process == "file not found":
            # If the ipcc is note downloadable, stops the progress bar and pops an error
            logger.error("User have requested a bundle that is not avaliable")
            progress_bar.stop()
            progress_bar.destroy()
            progress_label.destroy()
            message = textwrap.dedent(
                f"""\
            Your requested bundle:

            iPhone model: {product_type}
            iPhone version: {product_version}
            Bundle: {selected_bundle}
            Container: {replace_perc20(selected_container)}

            is not available!

            It either hasn't been downloaded from the server or you selected an unsupported bundle.

            This error has been sent to the developer for further investigation.
            """
            )
            arabic_message = renderBiDiText(
                textwrap.dedent(
                    f"""\
            :الحزمة التي طلبتها

            {product_type} :نوع
            {product_version} :إصدار
            {selected_bundle} :الحزمة
            {replace_perc20(selected_container)} :الحاوية

            غير متاحة!

            إما أنها لم تُنزل من الخادم بعد أو أنك اخترت حزمة غير مدعومة لجهازك

            تم إرسال هذا الخطأ إلى المطور للمزيد من التحقيق
            """
                )
            )

            messagebox.showerror(
                "Bundle not Found", arabic_message if arabic else message
            )
            return

        elif download_process == "you can't download any more today":
            progress_bar.stop()
            progress_bar.destroy()
            progress_label.destroy()
            messagebox.showerror(
                "limited", "you can't download any more today, try tomorrow"
            )
            logger.error(
                "you've been rate limited, you only have 3 times a day, you can't download any more today"
            )

            return

        # Goes through the connected device, if it is a new phone, would display the usage
        for new_iPhone in new_iPhones:
            if not product_type == new_iPhone:
                continue
            logger.info("User have a new iPhone")
            messagebox.showinfo(
                "Instructions",
                arabic_new_iphone_message if arabic else new_iPhone_message,
            )
            is_new_iPhone = True
        remove_bundle_file: str = os.path.join(
            ".", "resources", "removes_ipcc", "Remove(default).ipcc"
        )

        # logger.info(f"URL: {url}")

        progress_label.config(
            text=(
                renderBiDiText("... حذف ملف الشبكه السابق")
                if arabic
                else "Removing Old IPCC ..."
            )
        )
        window.update_idletasks()  # Update the label text

        # Remove old IPCC file
        with managedProcess(
            [ideviceinstaller, "install", remove_bundle_file], **kwargs
        ) as remove_process:
            stdout = remove_process.communicate()[0]
            stderr = remove_process.communicate()[1]
            result = stdout + stderr

        # If validate is set, and it is not a new phone, it slows down a bit
        if DataBase.get(["validate"], [True], "injection")[0] and not is_new_iPhone:
            sleep(
                20
            )  # Why?, well some devices need sometime to process the removal, so it waits for that
        else:
            # Else fast, because it is not needed to check
            sleep(7)

        if "Could not connect to lockdownd. Exiting." not in result:
            # Colors the logs
            if "SUCCESS: " in result:
                color = "green"
            elif "Install: Complete" in result:
                color = "green"
                result = renderBiDiText("تم حذف الملف السابق") if arabic else result
            elif "ERROR: " in result:
                logger.error(
                    f"An error happened in the removal, error: {result}, stack: {getStack()}"
                )
                color = "red"
            elif "No device found" in result:
                color = "red"
                result = (
                    renderBiDiText("لم يتم العثور على جهاز متصل")
                    if arabic
                    else "No device found"
                )
            else:
                color = "grey"

            log_text.tag_configure(color, foreground=color)
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, f"\n{result}\n", color)
            log_text.see(tk.END)
        else:
            logger.error("Trust error")
            messagebox.showerror(
                "Trust Error",
                (
                    renderBiDiText("يرجى اعادة تركيب الجهاز وحاول مره اخرى")
                    if arabic
                    else "Please reconnect the usb and try again"
                ),
            )
            progress_frame.destroy()

        # Sets up a temporary path for the selected .ipcc file to be downloaded to
        with TemporaryDirectory() as temp_dir:
            logger.debug(f"Temporary directory for the .ipcc: {temp_dir}")
            progress_label.config(
                text=(
                    renderBiDiText(
                        f"... {product_type} لجهاز  {selected_bundle} تحميل "
                    )
                    if arabic
                    else f"Downloading {selected_bundle} for {product_type}..."
                )
            )
            window.update_idletasks()

            # Gets the current directory and saves it for later
            last_dir = os.getcwd()

            # We go to the temporary directory so it would download there (can be used in other ways, but I find this the best for cross-platform)
            os.chdir(temp_dir)

            # download_process = subprocess.Popen(
            #     ["curl", "-L", "-OJL", url], **kwargs, universal_newlines=True
            # )
            ipcc_file_name = f"{replace_space(product_type)}_iOS_{product_version}_{selected_bundle}.ipcc"

            with open(ipcc_file_name, "wb") as ipcc_file:
                ipcc_file.write(download_process)

            # ipcc_file = io.BytesIO(download_process)

            # Now we go back so we can continue with the rest
            os.chdir(last_dir)

            # total_size = None
            # while True:
            #     # Read stderr stream
            #     output = download_process.stderr.readline().strip()
            #     if output == "" and download_process.poll() is not None:
            #         break

            #     # Parse progress information
            #     if " % " not in output:
            #         continue
            #     parts = output.split()
            #     # Ensure that the line contains enough parts to parse progress information
            #     if not len(parts) >= 9:
            #         continue
            #     # Check if the parts represent valid numbers before converting
            #     if not parts[1].isdigit() and not parts[6].isdigit():
            #         continue
            #     total_size = int(parts[1])
            #     downloaded = int(parts[6])
            #     progress = int((downloaded / total_size) * 100)
            #     progress_bar["value"] = progress
            #     window.update_idletasks()

            # Wait for the download process to finish
            # if download_process.wait() == 0:
            #     download_process.stdout.close()
            #     download_process.stderr.close()
            #     download_process.terminate()
            #     download_process.wait()

            # Extract the downloaded file path
            downloaded_file_path = os.path.join(temp_dir, ipcc_file_name)

            # Update progress label
            progress_label.config(
                text=(
                    renderBiDiText(f"{product_type} الى {selected_bundle} ادخال ")
                    if arabic
                    else f"Injecting {selected_bundle}.IPCC to {product_type}"
                )
            )
            window.update_idletasks()

            if DataBase.get(["validate"], [True], "injection")[0] and not is_new_iPhone:
                # If validate is set and is not a new iPhone, it would start the system logger right before injecting
                log_queue = []
                stop_event = Event()
                startThread(
                    target=lambda: readSysLog(log_queue, stop_event),
                    name="read syslog",
                    daemon=False,
                )

            # Inject .ipcc
            with managedProcess(
                [ideviceinstaller, "install", downloaded_file_path], **kwargs
            ) as injecting_process:
                stdout = injecting_process.communicate()[0]
                stderr = injecting_process.communicate()[1]
                result = stdout + stderr

            if "Could not connect to lockdownd. Exiting." not in result:
                # Red if error, Green if success
                if "SUCCESS: " in result:
                    color = "green"
                elif "Install: Complete" in result:
                    color = "green"
                    result = (
                        renderBiDiText(f"بنجاح {selected_bundle} تم تثبيت ملف ال ")
                        if arabic
                        else result
                    )
                elif "ERROR: " in result:
                    logger.error(
                        f"An error accoured in the injection of the file, error: {result}, stack: {getStack()}"
                    )
                    color = "red"
                elif "No device found":
                    color = "red"
                    result = (
                        renderBiDiText("لم يتم العثور على جهاز متصل")
                        if arabic
                        else "No device found"
                    )
                else:
                    color = "grey"

                log_text.tag_configure(color, foreground=color)
                log_text.insert(
                    tk.END,
                    (
                        renderBiDiText("------⸻⸻الإدخال⸻⸻------")
                        if arabic
                        else "------⸻⸻Injecting⸻⸻------"
                    ),
                )
                log_text.insert(tk.END, f"\n{result}\n", color)
                log_text.see(tk.END)

            if DataBase.get(["validate"], [True], "injection")[0] and not is_new_iPhone:
                progress_bar.stop()
                progress_bar.destroy()
                progress_label.destroy()
                window.update_idletasks()

                # Create new progress bar for validation
                validate_progress_frame = tk.Frame(window, bg=medium_color)
                validate_progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                validate_progress_label = tk.Label(
                    validate_progress_frame,
                    text=(
                        renderBiDiText(".. التحقق من الإدخال")
                        if arabic
                        else "Validating..."
                    ),
                    font=(getFont(), 14),
                    bg=medium_color,
                    fg=text_color,
                )
                validate_progress_label.pack(pady=5)
                validate_progress_bar = Progressbar(
                    validate_progress_frame,
                    orient="horizontal",
                    length=300,
                    mode="determinate",
                    style="Custom.Horizontal.TProgressbar",
                )
                validate_progress_bar.pack(pady=5)

                validate_progress_bar["maximum"] = 40
                for second in range(40):
                    validate_progress_bar["value"] = second + 1
                    window.update_idletasks()
                    sleep(1)

                # Collect logs from the syslog thread and stop it
                logs_result = "\n".join(log_queue)
                stop_event.set()
            else:
                # Stops and destroy the progress frame
                progress_bar.stop()
                progress_frame.destroy()

            # else:
            #     # If the download process failed
            #     logger.error("Could not download the file")
            #     window.update_idletasks()

            # This deletes the temp directory once done with it, over time, it can get a lot of temporary folders
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for _dir in dirs:
                    os.rmdir(os.path.join(root, _dir))
            os.rmdir(temp_dir)

        # Validate the injection by checking the logs
        if DataBase.get(["validate"], [True], "injection")[0] and not is_new_iPhone:
            # Only if it is not empty
            if logs_result is not None or logs_result == "":
                # If the line "SIM is ready" in the logs, that means it is working
                if "SIM is ready" in logs_result:
                    logger.success("SIM is ready, injection was successful.")

                    log_text.tag_configure("green", foreground="green")
                    log_text.insert(
                        tk.END,
                        (
                            renderBiDiText("----⸻⸻التحقق⸻⸻----")
                            if arabic
                            else "----⸻⸻Validatation⸻⸻----"
                        ),
                    )
                    log_text.insert(
                        tk.END,
                        (
                            renderBiDiText("\n الإدخال تم ينجاح \n")
                            if arabic
                            else "\nInjection successful. SIM is ready.\n"
                        ),
                        "green",
                    )
                    log_text.see(tk.END)
                    asyncio.run(
                        sendData("injection", device=product_type, success=True)
                    )
                else:
                    logger.error("SIM is not ready, injection failed.")

                    log_text.tag_configure("red", foreground="red")
                    log_text.insert(
                        tk.END,
                        (
                            renderBiDiText("----⸻⸻التحقق⸻⸻----")
                            if arabic
                            else "----⸻⸻Validatation⸻⸻----"
                        ),
                    )
                    log_text.insert(
                        tk.END,
                        (
                            renderBiDiText("\n فشل الإدخال \n")
                            if arabic
                            else "\nInjection failed. SIM is not ready.\n"
                        ),
                        "red",
                    )
                    log_text.see(tk.END)
                    asyncio.run(
                        sendData("injection", device=product_type, success=False)
                    )
            else:
                logger.info("Could not validate the injection process")
                log_text.tag_configure("grey", foreground="grey")
                log_text.insert(
                    tk.END,
                    (
                        renderBiDiText("----⸻⸻التحقق⸻⸻----")
                        if arabic
                        else "----⸻⸻Validatation⸻⸻----"
                    ),
                )
                log_text.insert(tk.END, "\nCould not validate\n", "grey")
                log_text.see(tk.END)

            validate_progress_bar.destroy()
            validate_progress_label.destroy()
        window.update_idletasks()

        # This is a just-in-case, if you have a new phone, it would ask if you want to restart the device
        for new_iPhone in new_iPhones:
            if product_type != new_iPhone:
                continue
            if download_process.wait() != 0:
                continue
            if not messagebox.askyesno(
                "Restart",
                (
                    renderBiDiText(
                        f"هل تريد اعادة الجهاز؟ \n\n قد تحتاج ل اعادة التشغيل  ،{product_type} يبدو ان لديك "
                    )
                    if arabic
                    else f"Looks like you have {product_type}, you might need to restart it\n\n Do you want to restart your iPhone?"
                ),
            ):
                logger.info("User declined the restart of his new iPhone")
                continue

            with managedProcess(
                [idevicediagnostics, "restart"], **kwargs
            ) as restart_process:
                stdout = restart_process.communicate()[0]
                stderr = restart_process.communicate()[1]
                if stdout:
                    logger.debug(stdout)
                elif stderr:
                    logger.warning(stderr)

    finally:
        # And finaly activates the button
        DataBase.add(["running"], [False], "injection")


def injection(window: tk.Tk, log_text: tk.Text) -> None:
    """
    Remove old IPCC files and inject the selected one into the device.

    Args:
        window (tk.Tk): The tkinter window.
        log_text (tk.Text): The text widget for logger.
        selected_bundle (str): The selected bundle name.
        selected_container (str): The selected option name.
    """

    # The thread has to be run from here, or the progress bar won't work well
    startThread(
        lambda: removingAndInjectingIPCC(window, log_text), "removingAndInjectingIPCC"
    )


def injectFromFile(log_text) -> None:
    """
    Injects the selected ipcc file manually
    """

    filepath = filedialog.askopenfilename(
        initialdir="~/Downloads",
        title=renderBiDiText("إختيار ملف شبكه") if arabic else "Select IPCC file",
        filetypes=(
            (renderBiDiText("ملف شبكه") if arabic else "IPCC Files", "*.ipcc"),
            (renderBiDiText("جميع الملفات") if arabic else "All Files", "*.*"),
        ),
    )

    if filepath:
        with managedProcess(
            [ideviceinstaller, "install", filepath], **kwargs
        ) as inject_from_file_process:
            # pass
            stdout = inject_from_file_process.communicate()[0]
            stderr = inject_from_file_process.communicate()[1]
            result = stdout + stderr
            # Colors the logs
            if "SUCCESS: " in result:
                color = "green"
            elif "Install: Complete" in result:
                color = "green"
                result = f"تم تثبيت الملف \n {filepath}\n بنجاح"
            elif "ERROR: " in result:
                logger.error(
                    f"An error happened in the manual inject, error: {result}, stack: {getStack()}"
                )
                color = "red"
            elif "No device found" in result:
                color = "red"
                result = "لم يتم العثور على جهاز متصل" if arabic else "No device found"
            else:
                color = "grey"

            log_text.tag_configure(color, foreground=color)
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, f"\n{result}\n", color)
            log_text.see(tk.END)


def cleanRemove(window: tk.Tk, log_text: tk.Text) -> None:
    """
    Does a clean Network Configuration (aka IPCC) removal.
    It might be handy if the iPhone is cluttered with ipccs.

    Args:
        window: tk.Tk --> the tkinter window.
        log_text: tk.Text --> The text widget for logger
    """
    if not messagebox.askokcancel(
        "Clean Bundles",
        (
            renderBiDiText(
                'اضغط على "موافق" إذا كنت تريد البدء في إزالة الحزم القديمة على iPhone'
            )
            if arabic
            else 'Press "OK" if you want to start removing old bundles on the iPhone'
        ),
    ):
        return

    DataBase.add(["running"], [True], "injection")

    # Check if device is connected
    with managedProcess([ideviceinfo, "-s"], **kwargs) as proc:
        stdout = proc.communicate()[0]
        stderr = proc.communicate()[1]
        result = stdout + stderr
        if "No device found" in result:
            logger.warning(
                "There is was no device connected while doing a clean removal"
            )
            log_text.tag_configure("yellow", foreground="yellow")
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(
                tk.END,
                (
                    renderBiDiText("لم يتم العثور على جهاز متصل\n\n")
                    if arabic
                    else "\nNo device found, is it plugged in?\n"
                ),
                "yellow",
            )
            log_text.see(tk.END)
            return

    # Create custom style for the progress bar. It looks better
    style = Style()
    style.theme_use("clam")

    # Configure colors and appearance for the custom style
    style.configure(
        "Custom.Horizontal.TProgressbar",
        background=light_color,
        troughcolor="#FFFFFF",
        bordercolor=light_color,
        lightcolor=light_color,
        darkcolor=light_color,
        troughrelief="flat",
        troughborderwidth=9,  # No trough border
        borderwidth=0,  # No border
        relief="flat",  # Flat relief
    )

    # Create progress frame
    progress_frame = tk.Frame(window, bg=medium_color)
    progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Progress label
    progress_label = tk.Label(
        progress_frame,
        text="Progress:",
        font=(getFont()),
        bg=medium_color,
        fg=text_color,
    )
    progress_label.pack(pady=5)

    # Progress bar
    progress_bar = Progressbar(
        progress_frame,
        orient="horizontal",
        length=300,
        mode="determinate",
        style="Custom.Horizontal.TProgressbar",
    )
    progress_bar.pack(pady=5)

    removes = [
        "CellularSouth",
        "ChinaCN",
        "ChinaHK",
        "ChinaUSIM",
        "CWW",
        "default",
        "unknown",
        "USCellular",
    ]
    # Files to remove
    remove_bundles_files: List[str] = [
        os.path.join(".", "resources", "removes_ipcc", f"Remove({name}).ipcc")
        for name in removes
    ]

    total_files = len(remove_bundles_files)

    # Remove bundles and update progress
    for i, file_path in enumerate(remove_bundles_files, start=1):
        progress_label.config(
            text=(
                renderBiDiText(f"{total_files}/{i} :حذف الملفات السابق")
                if arabic
                else f"Removing Old IPCC: {i}/{total_files}"
            )
        )
        window.update_idletasks()  # Update the label text

        with managedProcess(
            [ideviceinstaller, "install", file_path], **kwargs
        ) as remove_proc:
            stdout = remove_proc.communicate()[0]
            stderr = remove_proc.communicate()[1]
            result = stdout + stderr

            if "SUCCESS: " in result:
                color = "green"
                result = (
                    renderBiDiText(f"{removes[i - 1]} تم حذف الملف السابق")
                    if arabic
                    else result
                )
            elif "Install: Complete" in result:
                color = "green"

                result = (
                    renderBiDiText(f"{removes[i - 1]} تم حذف الملف السابق")
                    if arabic
                    else result
                )
            elif "ERROR: " in result:
                logger.error(
                    f"There was an error in the clean removal process, error: {result}, stack: {getStack()}"
                )
                color = "red"
            elif "No device found":
                color = "red"
                result = (
                    renderBiDiText("لم يتم العثور على جهاز متصل") if arabic else result
                )
            else:
                color = "grey"
            if "SUCCESS: " in result:
                color = "green"

            log_text.tag_configure(color, foreground=color)
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, f"\n{result}\n", color)
            log_text.see(tk.END)

        progress_bar["value"] = (i / total_files) * 100
        window.update_idletasks()

    # Destroy progress frame
    progress_frame.destroy()

    DataBase.add(["running"], [False], "injection")


def disableIfRunning(button: tk.Button, window: tk.Tk) -> None:
    """
    Disables the button if the user is injecting an ipcc to avoid multi injecting


    Args:
        button: tk.Button
        window: tk.Tk

    """
    while not terminate.is_set():
        plugged = DeviceManager().checkIfPlugged()

        if DataBase.get(["running"], [False], "injection")[0]:
            button.config(state=tk.DISABLED)
        else:
            button.config(state=tk.NORMAL if plugged else tk.DISABLED)
        sleep(0.5)
        window.update_idletasks()
