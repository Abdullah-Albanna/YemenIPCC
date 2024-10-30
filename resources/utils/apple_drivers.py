"""
checks if apple drivers on Windows are installed or not, and also installs them if not
"""

import subprocess
from typing import Literal
from itertools import chain
import tempfile
import httpx
from pathlib import Path
import shutil
import tkinter as tk
from tkinter.ttk import Progressbar, Style
import asyncio

import time

from utils.error_codes import ErrorCodes
from database.db import DataBase
from utils.logger_config_class import YemenIPCCLogger
from utils.messageboxes import MessageBox

from utils.managed_process import managedProcess
from utils.is_admin import isAdmin
from utils.get_os_lang import isItArabic
from utils.set_font import getFont
from utils.errors_stack import getStack

arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]
medium_color, light_color, text_color = DataBase.get(
    ["medium", "light", "text"], ["#0a1750", "#3b56bc", "white"], "colors"
)
logger = YemenIPCCLogger().logger


class AppleDrivers:
    def __init__(self, parent: tk.Tk):
        self.apple_drivers: dict = {
            "AppleMobileDeviceSupport64.msi": "https://drivers.abdurive.online/AppleMobileDeviceSupport64.msi",
            "apple_usb_driver.cab": "https://drivers.abdurive.online/apple_usb_driver.cab",
            "apple_tethering_driver.cab": "https://drivers.abdurive.online/apple_tethering_driver.cab",
        }

        self.drivers = ["oem50.inf", "oem21.inf", "oem32.inf"]

        self.temp_path = self.getTemp()
        self.extraction_path = self.temp_path / "extracted_msi"
        self.msi_file_path = self.temp_path / "AppleMobileDeviceSupport64.msi"

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
        progress_frame = tk.Frame(parent, bg=medium_color)
        progress_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.label = tk.Label(
            progress_frame,
            font=(getFont(), 10),
            bg=medium_color,
            fg=text_color,
        )

        self.progress_bar = Progressbar(
            progress_frame,
            orient="horizontal",
            style="Custom.Horizontal.TProgressbar",
            length=300,
        )

        # self.schedular = sched.scheduler(time.time, time.sleep)

    @staticmethod
    def checkInstalledAppleDrivers() -> bool | Literal["maybe", "error"]:
        apple_drivers = 0

        with managedProcess(
            ["pnputil", "/enum-drivers"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        ) as proc:
            stdout = proc.stdout
            stderr = proc.stderr

        if stderr:
            logger.error(
                f"Couldn't parse for installed drivers, error: {stderr}, stack: {getStack()}"
            )

            return "error"

        # Splits the drivers from the stdout to a list with two new lines
        drivers = stdout.split("\n\n")

        # Gets the splitted drivers to be splitted again by lines, using the chain to reduce the loops
        drivers_lines = list(
            chain.from_iterable(driver.splitlines() for driver in drivers)
        )

        for line in drivers_lines:
            # Splits it in key value
            key_value = line.split(":")

            # Using a try except because sometimes there is an empty line
            try:
                if any(
                    value in key_value[1].strip() for value in ["Apple, Inc.", "Apple"]
                ):
                    apple_drivers += 1

            except Exception:
                ...

        # Usually Windows comes with 1 driver installed, which is the default one,
        # it's not enough, we need at least 2, preferably 4
        if apple_drivers <= 1:
            return False
        else:
            return True

    @staticmethod
    def getTemp():
        temp = tempfile.gettempdir()

        # We store every thing inside of this directoy
        temp_path = (Path(temp) / "apple_drivers").resolve()
        temp_path.mkdir(exist_ok=True)

        return temp_path

    async def installAppleDrivers(self):
        # Some drivers won't install unless you are running installing it as an administrator
        if not isAdmin():
            MessageBox().showerror(
                "Permission Error",
                "(error code: {})\n\n Permission denied, please re-run  the app as an administrator".format(
                    ErrorCodes.PERMISSION_DENIED.value
                ),
            )
            logger.warning(
                "Permission denied, you cannot install apple drivers unless running as an admin"
            )

            return

        self.label.pack(pady=5)
        self.progress_bar.pack(pady=5)

        self.label.config(text="Downloading Drivers..")

        await self._downloadDrivers()

        self.label.config(text="Extracting Drivers...")
        self.progress_bar.config(mode="determinate")
        self.progress_bar.start(interval=50)

        self._extractDrivers()

        self.label.config(text="Installing Extracted Drivers...")

        self._installExtractedDrivers()

        if MessageBox().askyesno("Clean up", "Would you like to clean up downloaded drivers?"):
            self._cleanupDrivers()

        self.progress_bar.stop()

        self.label.destroy()
        self.progress_bar.destroy()

    async def reinstallDrivers(self):
        if not isAdmin():
            MessageBox().showerror(
                "Permission Error",
                "(error code: {})\n\n Permission denied, please re-run  the app as an administrator".format(
                    ErrorCodes.PERMISSION_DENIED.value
                ),
            )
            return

        self.label.config(text="Deleting Old Drivers..")
        self.label.update_idletasks()

        for driver in self.drivers:
            with managedProcess(
                ["pnputil", "/delete-driver", driver, "/uninstall", "/force"],
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
            ) as proc:
                stderr = proc.stderr

                if stderr:
                    logger.warning(
                        f"Couldn't delete old drivers, driver name: {driver}, error: {stderr}, stack: {getStack()}"
                    )

                if proc.returncode == 0:
                    logger.success(f"Successfully deleteed {driver} driver")

        await self.installAppleDrivers()

    def _installExtractedDrivers(self):
        time.sleep(0.5)

        # Gets every file ending in .inf, which are the drivers to be installed
        cab_infs = self.temp_path.glob("*.inf")

        # We extracted the .msi files, because apparently there is some infs inside that should be installed,
        # but sometimes it doesn't
        msi_extracted_folder = (
            self.extraction_path / "Common Files" / "Apple" / "Mobile Device Support"
        )
        # We then get every inf inside every folder
        msi_infs = msi_extracted_folder.rglob("*.inf")

        # Installs the .msi file
        if self.msi_file_path.exists():
            with managedProcess(
                ["msiexec", "/i", str(self.msi_file_path), "/qn"],
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
            ) as proc:
                stderr = proc.stderr

                if stderr:
                    logger.error(
                        f"Error installing msi file {self.msi_file_path}, Error: {stderr}, stack: {getStack()}"
                    )

                if proc.returncode == 0:
                    logger.success(
                        "Successfully installed the AppleMobileDeviceSupport64.msi"
                    )

        # Installs the .cab drivers
        for inf in cab_infs:
            if inf.exists():
                with managedProcess(
                    ["pnputil", "/add-driver", str(inf), "/install"],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                ) as proc:
                    stderr = proc.stderr
                    if stderr:
                        logger.error(
                            f"Error installing {inf}: {stderr}, stack: {getStack()}"
                        )

                    if proc.returncode == 0:
                        logger.success(f"Successfully installed {inf} driver")

        # Installs the .msi's drivers from inside, oem50.inf comes from here
        for inf in msi_infs:
            with managedProcess(
                ["pnputil", "/add-driver", str(inf), "/install"],
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
            ) as proc:
                stderr = proc.stderr
                if stderr:
                    logger.error(
                        f"Error installing {inf}: {stderr}, stack: {getStack()}"
                    )

                if proc.returncode == 0:
                    logger.success(f"Successfully installed {inf} driver")

    def _extractDrivers(self):
        for dri_name, _ in self.apple_drivers.items():
            if dri_name.endswith(".cab"):
                with managedProcess(
                    ["expand.exe", "-F:*", (self.temp_path / dri_name), self.temp_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                ) as proc:
                    stderr = proc.stderr

                    if stderr:
                        logger.error(
                            f"Error extracting {dri_name}, error: {stderr}, stack: {getStack()}"
                        )

                    if proc.returncode == 0:
                        logger.success(f"Successfully expanded the {dri_name}")

        self.extraction_path.mkdir(exist_ok=True)

        if self.extraction_path.exists():
            command = f'msiexec /a "{str(self.msi_file_path)}" /qn TARGETDIR="{str(self.extraction_path)}"'

            with managedProcess(
                command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL
            ) as proc:
                stderr = proc.stderr

                if stderr:
                    logger.error(
                        f"Error extracting {self.msi_file_path}, error: {stderr}, stack: {getStack()}"
                    )

                if proc.returncode == 0:
                    logger.success(f"Successfully extracted the {self.msi_file_path}")

    async def _downloadDrivers(self):
        logger.debug("Starting downloading Apple drivers")

        timeout = httpx.Timeout(connect=15.0, read=15.0, pool=15.0, write=15.0)

        retries = 5

        for dri_name, url in self.apple_drivers.items():
            file_path = self.temp_path / str(dri_name)
            logger.debug(f"Drivers file path: {file_path}")

            downloaded_size = file_path.stat().st_size if file_path.exists() else 0

            logger.debug(
                f"resuming download, downloaded size: {downloaded_size}"
                if downloaded_size != 0
                else "Downloading from the beginning"
            )

            for attempt in range(retries):
                logger.debug(f"Started at attempt {attempt}")

                try:
                    async with httpx.AsyncClient(
                        follow_redirects=True, timeout=timeout
                    ) as client:
                        # Set the range header to resume downloads
                        headers = (
                            {"Range": f"bytes={downloaded_size}-"}
                            if downloaded_size
                            else None
                        )

                        headers_response = await client.head(url)

                        server_total_size = int(
                            headers_response.headers.get("Content-Length", 0)
                        )

                        if server_total_size == downloaded_size:
                            logger.debug(f"{dri_name} has already been downloaded")
                            break

                        logger.debug(f"Headers are {headers}")

                        async with client.stream(
                            "GET", url, headers=headers
                        ) as response:
                            # Check if the response status is OK or for partial content (206)
                            if response.status_code not in [200, 206]:
                                logger.error(
                                    f"Failed to download {dri_name}, status code: {response.status_code}"
                                )

                                break

                            total_size = (
                                server_total_size + downloaded_size
                                if server_total_size
                                else None
                            )

                            logger.debug(f"The file size is {total_size}")

                            # Use a larger chunk size for better performance
                            chunk_size = 1024 * 64  # 64KB

                            logger.debug(f"The chunk size is {chunk_size}")

                            # Update the progress bar's maximum size
                            self.progress_bar.config(
                                maximum=total_size if total_size else 100
                            )

                            # Open the file in append mode to resume downloading
                            with open(file_path, "ab") as driver:
                                async for chunk in response.aiter_bytes(
                                    chunk_size=chunk_size
                                ):
                                    if chunk:
                                        driver.write(chunk)
                                        downloaded_size += len(chunk)

                                        # Update progress bar and label
                                        percentage = (
                                            (downloaded_size / total_size) * 100
                                            if total_size
                                            else 0
                                        )
                                        file_size = round(
                                            (downloaded_size / pow(2, 20)), 2
                                        )  # Size in MB

                                        # Use after method for safe GUI updates
                                        self.label.after(
                                            0,
                                            self.label.config,
                                            {
                                                "text": f"Downloading Drivers {dri_name} ({file_size}MB) {percentage:.2f}%"
                                            },
                                        )
                                        self.label.after(
                                            0,
                                            self.progress_bar.config,
                                            {"value": downloaded_size},
                                        )

                            # If we finish downloading the file, break out of the attempt loop
                            break  # Successful download, exit retry loop

                except (httpx.TimeoutException, httpx.RequestError) as e:
                    logger.warning(f"Attempt {attempt + 1} failed with error: {e}")

                    await asyncio.sleep(1)

                    # If the last attempt fails, notify the user
                    if attempt == retries - 1:
                        self.progress_bar.destroy()
                        self.label.destroy()
                        MessageBox().showerror(
                            "Download Error",
                            "(error code: {}) \n\n couldn't download drivers, please retry".format(
                                ErrorCodes.TIMEOUT.value
                            ),
                        )
                        logger.error(
                            f"Download error, couldn't download drivers, error: {e}"
                        )

    def _cleanupDrivers(self):
        shutil.rmtree(self.temp_path)
