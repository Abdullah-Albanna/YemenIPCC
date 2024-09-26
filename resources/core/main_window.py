import tkinter as tk
import textwrap
import asyncio
import sys
import keyring
import tkthread
import webbrowser
import os
from tkinter import messagebox
from PIL import ImageTk
from .. import Button
from time import sleep
from tempfile import gettempdir
from typing import List

from ..database.db import DataBase
from ..utils.logger_config_class import YemenIPCCLogger
from .api import API
from ..utils.images import Images

from .changing_option import changeWhichOne, changeBundle
from ..checkers.check_for_update import checkForUpdateButton
from ..device_management.injection import cleanRemove
from ..device_management.repair import repairiPhone
from ..handles.send_data import sendData
from ..misc.temp_uuid import getUUID
from ..handles.exit_handle import handleExit
from ..arabic_tk.bidid import renderBiDiText
from ..utils.set_font import getFont
from ..misc.resize_dpi import DPIResize
from ..device_management.injection import injection, disableIfRunning, injectFromFile
from ..core.fixing_the_window import initialize
from ..thread_managment.thread_starter import startThread
from ..checkers.check_for_update import checkForUpdate
from ..checkers.check_for_internet import checkInternetConnection
from ..device_management.device_manager import updateButtonStateThreaded, updateLabelStateThreaded, DeviceManager
from ..utils.exit_unsupported_version import quitIfNotSupported
from .login_signup_screen import main_
from ..utils.splash_screen import splash
from ..utils.errors_stack import getStack
from ..utils.get_os_lang import isItArabic

from ..utils.get_system import system
from ..thread_managment.thread_terminator_var import terminate
from ..thread_managment.thread_terminator_var import terminate_splash_screen
from ..config.version import CURRENT_VERSION

logger = YemenIPCCLogger().logger
arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]

dark_color, medium_color, light_color, text_color = DataBase.get(
    ["dark", "medium", "light", "text"],
    ["#030b2c", "#0a1750", "#3b56bc", "white"],
    "colors",
)

validate_status = DataBase.get(["validate"], [True], "injection")[0]


class LogScrollBar(tk.Scrollbar):
    def __init__(self, scroll_command, master=None, *args, **kwargs):
        # Use the global log_frame if master is not provided
        super().__init__(master, *args, **kwargs)
        self.configure(command=scroll_command, width=1, troughcolor=dark_color)
        self.pack(side=tk.RIGHT, fill="y")


class LogText(tk.Text):
    """
    Creates and configures the log text widget.
    """

    def __init__(self, master, *args, **kwargs):
        # Use the global log_frame if master is not provide
        super().__init__(master, *args, **kwargs)
        try:

            scrollbar = LogScrollBar(self.yview)
            self.configure(
                font=(getFont(), 12),
                wrap="word",
                bg=medium_color,
                fg=text_color,
                width=35,
                yscrollcommand=scrollbar.set,
            )
            self.pack(side=tk.LEFT, fill="both")

        except Exception as e:
            logger.error(f"An error occurred while creating the log text, error: {e}, error stack: {getStack()}")


class RadioButton(tk.Radiobutton):
    """
    Creates radio buttons for selecting which option and bundle to choose from.
    """

    def __init__(
            self,
            which_one_frame,
            bundles_frame,
            which_one: List[str],
            bundles: List[str],
            x: tk.IntVar,
            y: tk.IntVar,
            log_text,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.which_one_frame = which_one_frame
        self.bundles_frame = bundles_frame
        self.which_one = which_one
        self.bundles = bundles
        self.x = x
        self.y = y
        self.log_text = log_text
        self.create_radios()

    def create_radios(self):
        try:

            for index in range(len(self.which_one)):
                self.radio_which_one_buttom: tk.Radiobutton = tk.Radiobutton(
                    self.which_one_frame,
                    text=self.which_one[index],
                    variable=self.y,
                    value=index,
                    font=(getFont(), 15),
                    padx=33,
                    compound="top",
                    indicatoron=1,
                    activebackground=text_color,
                    bg=dark_color,
                    fg=text_color,
                    selectcolor=light_color,
                    command=lambda: changeWhichOne(
                        self.log_text, self.which_one, self.y
                    ),
                    width=10,
                )
                self.radio_which_one_buttom.pack(anchor=tk.NE, fill="both")

            # Create radio buttons for bundles
            for index in range(len(self.bundles)):
                self.radio_button: tk.Radiobutton = tk.Radiobutton(
                    self.bundles_frame,
                    text=self.bundles[index],
                    variable=self.x,
                    value=index,
                    font=(getFont(), 20),
                    padx=33,
                    compound="left",
                    indicatoron=0,
                    activebackground=text_color,
                    bg=dark_color,
                    fg=text_color,
                    selectcolor=light_color,
                    command=lambda: changeBundle(self.log_text, self.bundles, self.x),
                    width=10,
                )
                self.radio_button.pack(anchor=tk.NW, fill="both", expand=True)

        except Exception as e:
            logger.error(
                f"An error occurred while creating the radio buttons, error: {e}, error stack: {getStack()}"
            )


class Frames(tk.Frame):
    def __init__(
            self,
            master,
            bg=dark_color,
            bd=3,
            relief=tk.SUNKEN,
            padx=20,
            pady=20,
            *args,
            **kwargs,
    ):
        super().__init__(
            master, bg=bg, bd=bd, relief=relief, padx=padx, pady=pady, *args, **kwargs
        )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_version = CURRENT_VERSION
        self.UUID = getUUID()
        self.withdraw()

        windowCreation(self)
        
        tkthread.call(splash)

        asyncio.run(self.loginVerify())

        self.focus()
        self.tempdir = (
            gettempdir()
            if system == "Windows"
            else os.path.join(os.path.expanduser("~/cache"))
        )
        self.bundles: List[str] = [
            "CellularSouthLTE",
            "USCellularLTE",
            "China",
            "ChinaUSIM",
            "ChinaHK",
            "CWW",
        ]
        self.which_one: List[str] = ["default.bundle", "unknown.bundle"]
        self.xintvar = tk.IntVar()
        self.yintvar = tk.IntVar()


        self.connected_status: tk.Label = tk.Label(
            self,
            text=renderBiDiText("غير متصل") if arabic else "Disconnected",
            font=(getFont(), DPIResize(35)),
            bg=medium_color,  # Light Blue > < Dark Blue
            fg="red",
        )
        self.connected_status.pack(anchor=tk.NW, side="top", fill="both")

        # Main inject injection_button creation
        self.injection_button: Button = Button(
            self,
            text=renderBiDiText("إدخال") if arabic else "Inject",
            font=(getFont(), DPIResize(30), "bold"),
            relief=tk.RAISED,
            command=lambda: injection(self, self.log_text),
            bd=10,
            padx=100,
            fg="green",
            bg=dark_color,  # Dark Blue
            activebackground=dark_color,  # Dark Blue
            activeforeground=light_color,  # Light Blue
            state=tk.DISABLED,
        )

        # Selector Frame
        self.bundles_frame = Frames(self)
        self.bundles_frame.pack(anchor=tk.NE, side="right", fill="both")

        # Which One Frame
        self.which_one_frame = Frames(self.bundles_frame)
        self.which_one_frame.pack(anchor=tk.NE, side="top", fill="y")

        # Log Frame
        self.log_frame = Frames(self, padx=-200)
        self.log_frame.pack(anchor=tk.NW, side="left", fill="both")

        # Frame for Other Widgets
        self.frame = Frames(self, padx=45)
        self.frame.pack(anchor=tk.N, fill="both", side="top")

        self.log_text = LogText(self.log_frame)

        self.containerTypeLabel(self.which_one_frame)

        MenuBar(self, self.log_text, self.current_version)

        RadioButton(
            self.which_one_frame,
            self.bundles_frame,
            self.which_one,
            self.bundles,
            self.xintvar,
            self.yintvar,
            self.log_text,
        )

        self.injection_button.pack(side="bottom", fill="both")

        self.runThreads()

        initialize(self)
        self.protocol(
            "WM_DELETE_WINDOW",
            lambda: [
                self.withdraw(),
                self.destroy(),
                sendData("active", active=False, uid=self.UUID),
                handleExit(),
            ],
        )

        try:
            self.mainloop()
        except KeyboardInterrupt:
            self.withdraw()
            sendData("active", active=False, uid=self.UUID)
            self.quit()
            self.destroy()
            handleExit()

    async def loginVerify(self):
        username: str = DataBase.get(["username"], [False], "account")[0]

        if not username:
            terminate_splash_screen.set()
            sleep(1)
            main_("SignupPage")

        if username and keyring.get_password("yemenipcc", username) is None:
            terminate_splash_screen.set()
            sleep(1)
            main_("LoginPage")

        elif username:
            if not checkInternetConnection():
                messagebox.showerror("No Internet", 
                                     renderBiDiText("لايوجد اتصال بالانترنت") if arabic
                                    else "Make sure to connect to the internet first")
            
                terminate_splash_screen.set()
                sys.exit(1)
            
            try:
                response = await API().refreshToken(
                    keyring.get_password("yemenipcc", username), username
                )

                if response == "please get a new token":
                    terminate_splash_screen.set()
                    sleep(1)
                    main_("LoginPage")
                elif response == "success":
                    pass
                else:
                    terminate_splash_screen.set()
                    sleep(1)
                    messagebox.showerror(
                        "error",
                        (
                            renderBiDiText("ثم مشكله في الحساب")
                            if arabic
                            else "something went wrong with your account"
                        ),
                    )
                    sys.exit(1)

            except Exception as e:
                terminate_splash_screen.set()
                logger.error(f"somethin went wrong, error: {e}, stack: {getStack()}")
                sleep(1)
                messagebox.showerror(
                    "error",
                    (
                        renderBiDiText("حصلت مشكله، حاول لاحقا")
                        if arabic
                        else "something went wrong, try again later"
                    ),
                )
                sys.exit(1)

    def runThreads(self):

        startThread(
            lambda: disableIfRunning(self.injection_button, self), "disableIfRunning"
        )
        startThread(lambda: checkForUpdate(self.current_version), "checkForUpdate")
        updateButtonStateThreaded(
            self,
            self.frame,
            self.injection_button,
            self.log_text,
            self.connected_status,
        )
        updateLabelStateThreaded(
            self,
            self.frame,
            self.injection_button,
            self.log_text,
            self.connected_status,
        )
        startThread(self.updateActivity, "updating activity")
        startThread(
            lambda: quitIfNotSupported(self, self.current_version, self.UUID),
            "quitIfNotSupported",
        )
        startThread(lambda: sendData("app opens"), "Send active status")

    def updateActivity(self) -> None:
        """
        Updates the active status on the server on every 100 seconds, just to know how many actives there are.
        """
        while True:
            sendData("active", active=True, uid=self.UUID)
            if terminate.is_set():
                break
            sleep(2)

    def containerTypeLabel(self, which_one_frame):
        """
        Creates a label to indicate the type of .ipcc
        """
        tk.Label(
            which_one_frame,
            text=renderBiDiText("نوع الحزمة") if arabic else "Container Type:",
            font=(getFont(), 15),
            bg=dark_color,
            fg=text_color,
        ).pack(side="top", fill="both")


def windowCreation(window: tk.Tk) -> None:
    """
    Configures the main window.

    Args:
        window (tk.Tk): The main window.
    """
    try:
        # Gets the resolution of the device and set it to it and subtract from it a little so it won't go full screen
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        logger.debug(f"Screen resolution: {screen_width}:{screen_height}")
        window.geometry(f"{round(screen_width * 0.80)}x{round(screen_height * 0.80)}")
        window.minsize(
            width=round(screen_width * 0.70), height=round(screen_height * 0.70)
        )

        window.title("Yemen IPCC - by Abdullah Al-Banna")
        window.config(background=dark_color)  # Dark Blue

        icon = ImageTk.PhotoImage(
            Images.YemenIPCC_png,
            master=window,
        )

        window.iconphoto(True, icon)
        window.withdraw()

        logger.debug("Made the window")
    except Exception:
        logger.error(f"An error occurred while creating the window, error: {getStack()}")


class MenuBar(tk.Menu):
    """
    Creates and configures the menu bar.
    """

    def __init__(self, master, log_text, current_version, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.current_version = current_version
        self.master.config(menu=self, bg=medium_color)
        # self.validate_var = tk.BooleanVar(value=True)
        self.validate_var = validate_status

        # Create and add menus
        self.filemenu = self.addMenu(renderBiDiText("ملف") if arabic else "File")
        self.toolsmenu = self.addMenu(renderBiDiText("أدوات") if arabic else "Tools")
        self.languagemenu = self.addMenu(
            renderBiDiText("لغة") if arabic else "Language"
        )
        self.accountmenu = self.addMenu(
            renderBiDiText("الحساب") if arabic else "Account"
        )
        self.helpmenu = self.addMenu(renderBiDiText("مساعدة") if arabic else "Help")

        self.addCommand(
            self.filemenu,
            label=renderBiDiText("فتح") if arabic else "open",
            command=lambda: injectFromFile(log_text),
        )

        # It looks bad in Macs :(
        if system != "Mac":
            self.filemenu.add_separator()
            self.addCommand(
                self.filemenu,
                label=renderBiDiText("خروج") if arabic else "exit",
                command=lambda: [
                    self.master.withdraw(),
                    self.master.destroy(),
                    sendData("active", active=False, uid=getUUID()),
                    handleExit(),
                ],
            )

        self.addCommand(
            self.toolsmenu,
            label=renderBiDiText("تنضيف") if arabic else "clean",
            command=lambda: cleanRemove(self.master, log_text),
        )

        self.addCommand(
            self.toolsmenu,
            label=renderBiDiText("إعادة الاقتران") if arabic else "re-pair",
            command=lambda: repairiPhone(log_text),
        )

        # Add a checkbutton to the Tools menu
        self.toolsmenu.add_checkbutton(
            label=renderBiDiText("تحقق") if arabic else "validate",
            font=(getFont(), 14 if system == "Mac" or system == "Linux" else 10),
            variable=self.validate_var,
            command=lambda: self.onValidateToggle(self.validate_var),
        )

        self.toolsmenu.add_separator()

        self.addCommand(
            self.toolsmenu,
            label=renderBiDiText("إعادة التشغيل") if arabic else "restart",
            command=lambda: DeviceManager(log_text=log_text).systemActions("restart"),
        )

        self.addCommand(
            self.toolsmenu,
            label=renderBiDiText("إيقاف التشغيل") if arabic else "shutdown",
            command=lambda: DeviceManager(log_text=log_text).systemActions("shutdown"),
        )

        self.toolsmenu.add_separator()

        self.addCommand(
            self.toolsmenu,
            label=(
                renderBiDiText("البحث عن تحديث جديد") if arabic else "check for updates"
            ),
            command=lambda: checkForUpdateButton(self.current_version),
        )
        self.addCommand(
            self.languagemenu,
            label=renderBiDiText("تبديل اللغه") if arabic else "switch languages",
            command=self.switchLanguage,
        )

        self.addCommand(
            self.accountmenu,
            label=renderBiDiText("معلومات الحساب") if arabic else "account info",
            command=lambda: asyncio.run(self.showAccountInfo()),
        )

        self.accountmenu.add_separator()

        self.addCommand(
            self.accountmenu,
            label=renderBiDiText("تسجيل الخروج") if arabic else "logout",
            command=self.triggerLogOut,
        )

        self.addCommand(
            self.helpmenu,
            label=renderBiDiText("صفحتي على الجيت هب") if arabic else "github",
            command=lambda: webbrowser.open_new_tab(
                "https://github.com/Abdullah-Albanna/YemenIPCC"
            ),
        )

        if system != "Mac":
            self.helpmenu.add_separator()
            arabic_help = textwrap.dedent(
                renderBiDiText(
                    f"""تطبيق بسيط لأتمتة عملية إدخال ملفات الشبكة \n إلى أجهزة الايفون في اليمن
\n
المؤلف: عبدالله البناء
 الإصدار: {current_version}
        """
                )
            )

            # arabic_help = textwrap.wrap(arabic_help, width=5)  # Adjust the width to fit your Tkinter widget
            english_help = f"Yemen IPCC \n\n A simple app to automate the process of injecting the network configuration files (.ipcc) to the iPhone devices in Yemen\n\n\n author: Abdullah Al-Banna \n version: {current_version}"

            self.addCommand(
                self.helpmenu,
                label=renderBiDiText("حول") if arabic else "about",
                command=lambda: messagebox.showinfo(
                    "حول" if arabic else "About",
                    arabic_help if arabic else english_help,
                ),
            )

    def addCommand(self, menu: tk.Menu, label, command):
        menu.add_command(
            label=label,
            font=(getFont(), 14 if system == "Mac" or system == "Linux" else 10),
            command=command,
        )

    def addMenu(self, label):
        menu = tk.Menu(
            self,
            tearoff=0,
            font=(getFont(), 14 if system == "Darwin" or system == "Linux" else 10),
        )
        self.add_cascade(
            label=label,
            menu=menu,
            font=(getFont(), 14 if system == "Darwin" or system == "Linux" else 10),
        )
        return menu

    def triggerLogOut(self):
        keyring.delete_password(
            "yemenipcc", DataBase.get(["username"], [False], "account")[0]
        )
        messagebox.showinfo("logout", renderBiDiText("تم تسجيل الخروج بنجاح") if arabic else "successfully logged out")

        self.restart()

    async def showAccountInfo(self):
        user = await API().grabUserInfo()
        message = textwrap.dedent(
            f"""\
    username: {user.get("username")}
    premium: {"no" if not user.get("premium") else "yes"}
    downloads left: {user.get("download_left")}
    created at: {user.get("created_at")}
"""
        ).replace("T", " ")

        arabic_message = renderBiDiText(
            textwrap.dedent(
                f"""
    اسم المستخدم: {user.get("username")}
    مميز: {"لا" if not user.get("premium") else "نعم"}
    التنزيلات المتبقية: {user.get("download_left")}
    تم الإنشاء في: {user.get("created_at")}
    """
            )
        ).replace("T", " ")

        messagebox.showinfo("user info", arabic_message if arabic else message)

    def onValidateToggle(self, validate_var):

        if validate_var:
            DataBase.add(["validate"], [True], "injection")
        else:
            if messagebox.askyesno(
                    "Disable Validation",
                    (
                            renderBiDiText(
                                "إيقاف التحقق سيجعل التطوير بطيئًا، يُوصى بتركه مفعلًا\n\n هل أنت متأكد أنك تريد تعطيله؟"
                            )
                            if arabic
                            else "Turning off validating would make development slow, it is recommended to leave it on\n\n Are you sure you want to disable it?"
                    ),
            ):
                DataBase.add(["validate"], [False], "injection")
            else:
                # validate_var.set(True)
                DataBase.add(["validate"], [True], "injection")

    def switchLanguage(self):

        if arabic:
            DataBase.add(["arabic"], [False], "app")
            self.restart()
        else:
            DataBase.add(["arabic"], [True], "app")
            self.restart()

    def restart(self):
        executeable = sys.executable

        self.master.withdraw()
        self.master.destroy()
        if getattr(sys, "frozen", False):
            os.execl(executeable, *sys.argv)
        os.execl(executeable, executeable, *sys.argv)
