import subprocess
from typing import Literal
from itertools import chain
import tempfile
import httpx
from pathlib import Path
import shutil
import tkinter as tk
from tkinter.ttk import Progressbar, Style
from tkinter import messagebox

import time
import sched

from .error_codes import ErrorCodes
from ..database.db import DataBase

from .managed_process import managedProcess
from .is_admin import isAdmin
from .get_os_lang import isItArabic
from .set_font import getFont

arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]
medium_color, light_color, text_color = DataBase.get(
    ["medium", "light", "text"], ["#0a1750", "#3b56bc", "white"], "colors"
)

class AppleDrivers():
    def __init__(self, parent: tk.Tk):

        self.apple_drivers: dict = {
            "AppleMobileDeviceSupport64.msi": "http://127.104.138:50061/AppleMobileDeviceSupport64.msi",
            "apple_usb_driver.cab": "http://127.104.138:50061/apple_usb_driver.cab",
            "apple_tethering_driver.cab": "http://127.104.138:50061/apple_tethering_driver.cab",
        }
        
        self.temp_path = self.getTemp()

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

    
        self.label = tk.Label(progress_frame,            font=(getFont()), text="Download Drivers ...",           bg=medium_color,
            fg=text_color,)

        self.progress_bar = Progressbar(progress_frame, orient="horizontal", style="Custom.Horizontal.TProgressbar", length=300)

        # self.schedular = sched.scheduler(time.time, time.sleep)

    
    def checkInstalledAppleDrivers(self) -> bool | Literal["maybe", "error"]:
        apple_drivers = 0

        with managedProcess(["pnputil", "/enum-drivers"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as proc:
            stdout = proc.communicate()[0]
            stderr = proc.communicate()[1]

        if stderr:
            return "error"
        
        drivers =  stdout.split("\n\n")

        drivers_lines = list(chain.from_iterable(driver.splitlines() for driver in drivers))

        for line in drivers_lines:

            key_value = line.split(":")
            
            try:
                if any(value in key_value[1].strip() for value in ["Apple, Inc.", "Apple"]):
                    apple_drivers += 1

            except Exception: ...

        if apple_drivers <= 1:
            return False
        else:
            return True
        
    def getTemp(self):
        temp = tempfile.gettempdir()

        temp_path = (Path(temp) / "apple_drivers").resolve()
        temp_path.mkdir(exist_ok=True)
        
        return temp_path
    
    # def installAppleDrivers(self):
    #     self.schedular.enter(5, 1, self._installAppleDrivers)
    #     self.schedular.run()

    async def installAppleDrivers(self):
        
        if not isAdmin():
            messagebox.showerror("Permission Error", "(error code: {})\n\n Permission denied, please re-run  the app as an administrator".format(ErrorCodes.PERMISSION_DENIED.value))
            return
        
        # apple_drivers: dict = {
        #     "AppleMobileDeviceSupport64.msi": "https://www.apple.com/itunes/download/win64",
        #     "apple_usb_driver.cab": "https://catalog.s.download.windowsupdate.com/d/msdownload/update/driver/drvs/2020/11/01d96dfd-2f6f-46f7-8bc3-fd82088996d2_a31ff7000e504855b3fa124bf27b3fe5bc4d0893.cab",
        #     "apple_tethering_driver.cab": "https://catalog.s.download.windowsupdate.com/c/msdownload/update/driver/drvs/2017/11/netaapl_7503681835e08ce761c52858949731761e1fa5a1.cab",
        # }

        self.label.pack(pady=5)
        self.progress_bar.pack(pady=5)

        self._downloadDrivers()

        self.label.config(text="Extracting Drivers...")
        self.progress_bar.config(mode="determinate")
        self.progress_bar.start(interval=50)

        self._extractDrivers()

        self.label.config(text="Installing Extracted Drivers...")

        self._installExtractedDrivers()

        self._cleanupDrivers()

        self.progress_bar.stop()

        self.label.destroy()
        self.progress_bar.destroy()


    def _installExtractedDrivers(self):
        time.sleep(0.5)
        
        infs = self.temp_path.glob("*.inf")

        for dri_file in infs:
            with managedProcess(["pnputil", "/add-driver", dri_file], shell=False, stderr=subprocess.PIPE) as proc:
                stderr = proc.communicate()[1]

                if stderr:
                    return False

    def _extractDrivers(self):

        for dri_name, _ in self.apple_drivers.items():

            if dri_name.endswith(".cab"):
                with managedProcess(["expand.exe", "-F:*", (self.temp_path / dri_name), self.temp_path], shell=False, stderr=subprocess.PIPE) as proc:
                    stderr = proc.communicate()[1]

                    if stderr:
                        return False

    def _downloadDrivers(self):

        timeout = httpx.Timeout(None, connect=10.0, read=10.0, pool=10.0, write=10.0)

        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                for dri_name, url in self.apple_drivers.items():
                    
                    file_path = self.temp_path / dri_name

                    if dri_name == "AppleMobileDeviceSupport64.msi":
                        continue
                    
                    with client.stream("GET", url) as response:

                        total_size = int(response.headers.get('Content-Length', 0))

                        downloaded_size = 0
                        chunk_size = 1024 # 1KB

                        self.progress_bar.config(maximum=total_size)

                        with open(file_path, "wb") as driver:
                            for chunk in response.iter_bytes(chunk_size=chunk_size):
                                if chunk:
                                    
                                    percentage = (downloaded_size / total_size) * 100

                                    self.label.config(text=f"Downloading Drivers {dri_name} {percentage:.2f}%")
                                    self.progress_bar.config(value=downloaded_size)
                                    
                                    self.progress_bar.update_idletasks()

                                    downloaded_size += len(chunk)

                                    driver.write(chunk)

        except httpx.TimeoutException:
            self.progress_bar.destroy()
            self.label.destroy()

            messagebox.showerror("Timeout", "(error code: {}) \n\n drivers download timed out".format(ErrorCodes.TIMEOUT.value))

    def _cleanupDrivers(self):
        shutil.rmtree(self.temp_path)

# def installAppleDrivers():
#     script_url = "https://raw.githubusercontent.com/NelloKudo/Apple-Mobile-Drivers-Installer/main/AppleDrivInstaller.ps1"
#     cmd = [
#         "powershell.exe",
#         "-NoExit",
#         "-ExecutionPolicy",
#         "Bypass",
#         "-Command", 
#         f"Start-Process powershell -Verb RunAs -ArgumentList '-NoExit', '-ExecutionPolicy Bypass', '-Command irm {script_url} | iex'"
#     ]

#     with managedProcess(cmd, shell=False, stderr=subprocess.PIPE) as proc:
#         stderr = proc.communicate()[1]

#         if stderr:
#             return False