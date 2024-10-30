import tkinter as tk
import subprocess
from typing import Tuple, Dict
from time import sleep


from utils.logger_config_class import YemenIPCCLogger
from utils.get_bin_path import BinaryPaths
# from database.dict_control import DictControl
from database.db import DataBase
from core.idevice import iDevice

from thread_management.thread_starter import startThread
# from utils.managed_process import managedProcess
from misc.resize_dpi import DPIResize
from arabic_tk.bidid import renderBiDiText
from utils.set_font import getFont
# from utils.errors_stack import getStack
from utils.get_os_lang import isItArabic

from thread_management.thread_terminator_var import terminate
from utils.get_system import system


arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]
dark_color, text_color = DataBase.get(["dark", "text"], ["#030b2c", "white"], "colors")


logger = YemenIPCCLogger().logger

bin_paths = BinaryPaths().getPaths()

ideviceinfo = bin_paths["ideviceinfo"]
idevice_id = bin_paths["idevice_id"]
idevicepair = bin_paths["idevicepair"]
idevicediagnostics = bin_paths["idevicediagnostics"]
kwargs = bin_paths["kwargs"]


class DeviceManager:
    """
    A class to control the iPhone
    """

    def __init__(
        self, window=None, frame=None, button=None, log_text=None, connected_status=None
    ):
        self.window: tk.Tk = window
        self.frame: tk.Frame = frame
        self.button: tk.Button = button
        self.log_text: tk.Text = log_text
        self.connected_status: tk.Label = connected_status
        self.iPhoneType: tk.Label = None
        self.iPhoneVersion: tk.Label = None
        self.disconnected_label: tk.Label = None
        self.logged_product_type: str = ""
        self.logged_product_version: str = ""
        self.logged_errors = set()

    # def systemActions(self, action: str) -> None:
    #     """
    #     Controls the iPhone to restart or shutdown or even sleep
    #     """

        # with managedProcess([idevicediagnostics, action], **kwargs) as device_process:
        #     if device_process is None:
        #         return

        #     stdout = device_process.stdout
        #     stderr = device_process.stderr
        #     result = stderr + stdout

        #     if "ERROR" in result:
        #         color = "red"
        #         logger.warning(result)
        #     elif "No device found." in result:
        #         logger.debug(result)
        #         color = "yellow"
        #         result = (
        #             renderBiDiText("لم يتم العثور على جهاز متصل") if arabic else result
        #         )
        #     else:
        #         color = "green"
        #         logger.debug(result)

        #     self.log_text.tag_configure(color, foreground=color)
        #     self.log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        #     self.log_text.insert(tk.END, f"\n{result}\n", color)
        #     self.log_text.see(tk.END)

    # def validateDevice(self) -> bool:
    #     """
    #     Checks if the device is really paired
    #     """
    #     try:
    #         # Runs ideviceinfo, which is used to get the iPhone information, and catch the errors, if there is no, then it is good to go
    #         with managedProcess([ideviceinfo], **kwargs):
    #             pass
    #         return True
    #     except subprocess.CalledProcessError as e:
    #         error_message: str = e.stderr.strip()
    #         logger.error(
    #             f"An error occurred in the validation of the device, error: {error_message}, stack: {getStack()}"
    #         )
    #         if "Could not connect to lockdownd: SSL error (-5)" in error_message:
    #             return False
    #         elif "Device validation failed: unhandled error code -5" in error_message:
    #             self.connected_status.config(
    #                 text="Please Reconnect the USB and Trust Again", fg="red"
    #             )
    #             return False

    def extractValuesFromLog(self) -> Tuple[str, str] | None:
        """
        Extracts some information about the connected device
        """

        product_version: str = ""
        product_type: str = ""
        try:
            device_info = iDevice.deviceInfo()

            product_type = device_info.get("ProductType", "Unknown")
            product_version = device_info.get("ProductVersion", "Unknown")
            # # -s is short for "short", maybe
            # with managedProcess([ideviceinfo, "-s"], **kwargs) as device_info:
            #     if device_info is None:
            #         return
            #     stdout = device_info.stdout
            #     stderr = device_info.stderr

            #     if DictControl().shouldRun("idevice_info_stdout") and stdout:
            #         logger.debug(f"ideviceinfo stdout:\n\n {stdout}")

            #     if stderr:
            #         if "Could not connect to lockdownd" in stderr:
            #             # This occurres when you accept the restart dialog at the end of the injection, so we want to log once
            #             if DictControl().shouldRun("logged_lockdownd_error"):
            #                 logger.warning(
            #                     f"An error occurred in the extraction of the idevice info, error: {stderr}"
            #                 )
            #             return
            #         else:
            #             if "ERROR: No device found!":
            #                 DictControl().runAgain("idevice_info_stdout")
            #                 return
            #             else:
            #                 logger.warning(
            #                     f"An error occurred in the extraction of the idevice info, error: {stderr}"
            #                 )
            #                 return

            # output_lines: List[str] = stdout.splitlines() + stderr.splitlines()

            # # This one look for the iPhone type and its version, and saves it to the above variables
            # for line in output_lines:
            #     if "ProductVersion:" in line:
            #         product_version = line.split("ProductVersion:")[1].strip()  # The "1" is for the whitespace

            #     elif "ProductType:" in line:
            #         product_type = line.split("ProductType:")[1].strip()

            DataBase.add(
                ["iPhone_version", "iPhone_model"],
                [product_version, product_type],
                "iphone",
            )

            # This to make sure to show the iPhone information only once a plug
            if self.checkIfPlugged():
                if self.logged_product_type != product_type:
                    if product_type != "":
                        if self.logged_product_type != product_type:
                            logger.info(f"iPhone model: {product_type}")
                            self.logged_product_type = product_type
                    self.logged_product_type = product_type

                if self.logged_product_version != product_version:
                    if product_version != "":
                        if self.logged_product_version != product_version:
                            logger.info(f"iPhone version: {product_version}")
                            self.logged_product_version = product_version
                    self.logged_product_version = product_version

            else:
                self.logged_product_version = ""
                self.logged_product_type = ""

            # Creating a dictionary to convert machine id to a known name, used then for displaying what iPhone is connected
            product_type_mappings: Dict[str, str] = {
                "iPhone7,2": "iPhone 6",
                "iPhone7,1": "iPhone 6+",
                "iPhone8,1": "iPhone 6S",
                "iPhone8,2": "iPhone 6S+",
                "iPhone8,4": "iPhone SE.2016",
                "iPhone9,1": "iPhone 7",
                "iPhone9,2": "iPhone 7 Plus",
                "iPhone10,1": "iPhone 8",
                "iPhone10,2": "iPhone 8 Plus",
                "iPhone10,3": "iPhone X",
                "iPhone11,2": "iPhone XS",
                "iPhone11,4": "iPhone XS Max.China",
                "iPhone11,6": "iPhone XS Max",
                "iPhone11,8": "iPhone XR",
                "iPhone12,1": "iPhone 11",
                "iPhone12,3": "iPhone 11 Pro",
                "iPhone12,5": "iPhone 11 Pro Max",
                "iPhone12,8": "iPhone SE.2020",
                "iPhone13,1": "iPhone 12 Mini",
                "iPhone13,2": "iPhone 12",
                "iPhone13,3": "iPhone 12 Pro",
                "iPhone13,4": "iPhone 12 Pro Max",
                "iPhone14,4": "iPhone 13 Mini",
                "iPhone14,5": "iPhone 13",
                "iPhone14,2": "iPhone 13 Pro",
                "iPhone14,3": "iPhone 13 Pro Max",
                "iPhone14,6": "iPhone SE.2022",
            }

            if not product_type:
                product_type = "empty-iPhone-id"
            else:
                product_type = product_type_mappings.get(product_type, "Unsupported")
            DataBase.add(["iPhone_model_alt"], [product_type], "iphone")
        except subprocess.CalledProcessError as subpe:
            # Catching the error of the ideviceinfo, if it has errors then it is probably not trusted
            logger.warning(f"An error occurred, trust error, error: {subpe}")
            self.log_text.tag_configure("red", foreground="red")
            self.log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            self.log_text.insert(
                tk.END,
                "\nCommand 'ideviceinfo -s' returned non-zero exit status\n",
                "red",
            )
            self.log_text.see(tk.END)
            self.connected_status.config(text="Please Trust this Computer", fg="green")
            iDevice.pair()

        return product_version, product_type

    def checkIfPlugged(self) -> bool:
        """
        Checks if the device is plugged or not
        """

        try:
            # # This prints the iPhone id, whether it is trusted or not, which is good, we only want to know if it plugged or not
            # with managedProcess([idevice_id, "-l"], **kwargs) as result:
            #     if result is None:
            #         return False
            #     stdout = result.stdout
            #     stderr = result.stderr

            #     if stderr:
            #         if "Unable to retrieve device list!" not in stderr:
            #             if stderr not in self.logged_errors:
            #                 logger.error(
            #                     f"An error occurred in the checkIfPlugged, error: {stderr}, stack: {getStack()}"
            #                 )
            #                 self.logged_errors.add(stderr)
            #     return bool(stdout.strip())

            return iDevice.isPlugged()

        except subprocess.CalledProcessError:
            return False

    def updateButtonState(self) -> None:
        """
        Updates the button state, if the device is plugged it gets enabled, if not then no,

        if plugged and the injection is running then no
        """
        while True:
            if terminate.is_set():
                break

            plugged = self.checkIfPlugged()
            running = DataBase.get(["running"], [False], "injection")[0]

            if running and plugged:
                self.button.config(state=tk.DISABLED)
            elif not running:
                self.button.config(state=tk.NORMAL if plugged else tk.DISABLED)

            sleep(0.3)
            self.window.update_idletasks()

    def updateLabelState(self) -> None:
        """
        Configures the iPhone version and the iPhone type labels
        """

        while True:
            plugged = self.checkIfPlugged()

            # # if it is plugged and returns False on the validation, we need to trust the device
            # if not self.validateDevice() and plugged:
            #     self.log_text.tag_configure("red", foreground="red")
            #     self.log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            #     self.log_text.insert(
            #         tk.END,
            #         (
            #             renderBiDiText("\nفشل التحقق من الجهاز: رمز خطأ غير معالج -5\n")
            #             if arabic
            #             else "\nDevice validation failed: unhandled error code -5\n"
            #         ),
            #         "red",
            #     )
            #     self.log_text.see(tk.END)
            #     self.connected_status.config(
            #         text=(
            #             renderBiDiText("يرجى إعادة توصيل الجهاز ومنح الثقة")
            #             if arabic
            #             else "Please Reconnect the USB and Trust"
            #         ),
            #         fg="red",
            #     )
            #     sleep(1)
            #     # with managedProcess([f"{idevicepair}", "pair"], **kwargs):
            #     #     pass
            #     iDevice.pair()
            #     sleep(1)

            if plugged:
                # We don not want thoes to be global from the extractValuesFromLog because we need to to repeatedly know what device is connected
                product_version, product_type = self.extractValuesFromLog()

                self.connected_status.config(
                    text=renderBiDiText("متصل") if arabic else "Connected", fg="green"
                )

                # Because this function is in a while loop, we need a way of handling the labels from repeating and going on a long line
                if (
                    not self.iPhoneType
                ):  # This is like if the label is not empty, clear it
                    self.iPhoneType = tk.Label(
                        self.frame,
                        font=(getFont(), DPIResize(25)),
                        bg=dark_color,
                        fg=text_color,
                    )
                    self.iPhoneType.pack()

                if product_type == "empty-iPhone-id":
                    self.iPhoneType.config(
                        text=(
                            renderBiDiText("ربما يعاد التشغيل ؟")
                            if arabic
                            else "Maybe restarting?"
                        )
                    )

                elif product_type != "Unsupported":
                    self.iPhoneType.config(
                        text=(
                            renderBiDiText(f"{product_type} :النوع ")
                            if arabic
                            else f"iPhone Type: {product_type}"
                        )
                    )  # Then fill it again
                else:
                    self.iPhoneType.config(
                        text=renderBiDiText("غير مدعوم") if arabic else "Unsupported",
                        fg="grey",
                        font=(getFont(), DPIResize(21)),
                    )

                    DataBase.add(["running"], [True], "injection")

                if not self.iPhoneVersion:  # Same and so as the other
                    self.iPhoneVersion = tk.Label(
                        self.frame,
                        font=(getFont(), DPIResize(25)),
                        bg=dark_color,
                        fg=text_color,
                    )

                    self.iPhoneVersion.pack(fill="both")

                if product_type == "empty-iPhone-id":
                    self.iPhoneVersion.config(
                        text=(
                            renderBiDiText("او ايقاف تشغيل :)")
                            if arabic
                            else "Or shuting down :)"
                        )
                    )

                elif product_type != "Unsupported":
                    match system:
                        case "Windows":
                            arabic_text = f"{product_version} :الاصدار"
                        case "Mac":
                            arabic_text = f"الاصدار: {product_version} "
                        case "Linux":
                            arabic_text = renderBiDiText(f"الاصدار: {product_version} ")

                    self.iPhoneVersion.config(
                        text=(
                            arabic_text
                            if arabic
                            else f"iPhone Version: {product_version}"
                        )
                    )

                else:
                    self.iPhoneVersion.config(
                        text=(
                            renderBiDiText("لا حاجه لملف شبكه")
                            if arabic
                            else "Your Device Does not Need\n IPCC Files"
                        ),
                        fg="yellow",
                    )

                if self.disconnected_label:
                    self.disconnected_label.pack_forget()
                    self.disconnected_label = None

            else:
                self.connected_status.config(
                    text=renderBiDiText("غير متصل") if arabic else "Disconnected",
                    fg="red",
                )  # Same logic

                if self.iPhoneType:
                    self.iPhoneType.pack_forget()
                    self.iPhoneType = None
                if self.iPhoneVersion:
                    self.iPhoneVersion.pack_forget()
                    self.iPhoneVersion = None

                if not self.disconnected_label:
                    self.disconnected_label = tk.Label(
                        self.frame,
                        text=(
                            renderBiDiText("يرجى توصيل جهاز الايفون")
                            if arabic
                            else "Please connect your iPhone"
                        ),
                        font=(getFont(), DPIResize(30)),
                        bg=dark_color,
                        fg=text_color,
                    )

                    self.disconnected_label.pack()

            if terminate.is_set():
                break
            sleep(0.3)
            self.window.update_idletasks()  # And finally updates the window


# Both has to be running from here, if you don't, you'll get weird behavior
def updateButtonStateThreaded(
    window: tk.Tk,
    frame: tk.Frame,
    button: tk.Button,
    log_text: tk.Text,
    Stats: tk.Label,
) -> None:
    """
    Starts a thread to run "updateButtonState"

    has to be this way
    """

    startThread(
        lambda: DeviceManager(
            window, frame, button, log_text, Stats
        ).updateButtonState(),
        "updateButtonStateThreaded",
    )


def updateLabelStateThreaded(
    window: tk.Tk,
    frame: tk.Frame,
    button: tk.Button,
    log_text: tk.Text,
    Stats: tk.Label,
) -> None:
    """
    Starts a thread to run "updateLabelState"

    has to be this way
    """

    startThread(
        lambda: DeviceManager(
            window, frame, button, log_text, Stats
        ).updateLabelState(),
        "updateLabelStateThreaded",
    )
