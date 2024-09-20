import tkinter as tk
import re
import asyncio
from tkinter import messagebox
from PIL import ImageTk
from typing import Literal
from time import sleep


from .api import API
from ..utils.user_credentials import UserCredentials
from ..utils.gif_placer import AnimatedGIF
from ..utils.logger_config_class import YemenIPCCLogger
from ..database.db import DataBase
from ..utils.images import Images

from ..thread_managment.thread_starter import startThread
from ..handles.exit_handle import handleExit
from ..arabic_tk.bidid import renderBiDiText
from ..utils.errors_stack import getStack
from ..utils.get_os_lang import isItArabic

logger = YemenIPCCLogger().logger
arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]


class Circle:
    def __init__(self, canvas, color, posion: tuple):
        self.canvas = canvas
        self.circle_id = None
        self.circle_color = color
        self.circle_radius = 10
        self.circle_posion = posion

        self.draw_red_dot()

    def draw_red_dot(self):
        if self.circle_id:
            self.canvas.delete(self.circle_id)

        x, y = self.circle_posion
        self.circle_id = self.canvas.create_oval(
            x - self.circle_radius,
            y - self.circle_radius,
            x + self.circle_radius,
            y + self.circle_radius,
            fill=self.circle_color,
            outline=self.circle_color,
        )

    def set_position(self, position):
        self.circle_posion = position
        self.draw_red_dot()

    def set_color(self, color):
        self.circle_color = color
        self.draw_red_dot()


class LoginPage(tk.Frame):
    def __init__(self, parent, master):
        super().__init__(parent)
        self.master = master
        self.valid_username = False
        self.running = False

        self.canvas = tk.Canvas(
            self,
            bg="#101520",
            height=418,
            width=467,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )

        self.canvas.place(x=0, y=0)

        self.login_signup_button_image = ImageTk.PhotoImage(
            Images.login_signup_button_png
        )
        self.login_signup_hover_button_image = ImageTk.PhotoImage(
            Images.login_signup_hover_button_png
        )
        self.login_username_entry_image = ImageTk.PhotoImage(Images.login_entry_1_png)
        self.login_password_entry_image = ImageTk.PhotoImage(Images.login_entry_2_png)
        self.entry_bg_icon_image_1 = ImageTk.PhotoImage(
            Images.entry_bg_icon_image_1_png
        )
        self.entry_bg_icon_image_2 = ImageTk.PhotoImage(
            Images.entry_bg_icon_image_2_png
        )
        self.username_icon = ImageTk.PhotoImage(Images.username_icon_png)
        self.password_icon = ImageTk.PhotoImage(Images.password_icon_png)

        self.login_bg = ImageTk.PhotoImage(Images.login_background_png)

        self.canvas.create_image(238.0, 209.0, image=self.login_bg)

        self.canvas.create_text(
            170.0 if arabic else 148.0,
            29.0,
            anchor="nw",
            text=renderBiDiText("مرحبا بعودتك") if arabic else "Welcome Back",
            fill="#FFFFFF",
            # font=("Inter Bold", 24 * -1),
            font=("Arial", 24 * -1),
        )

        # self.login_button_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/login_button.png")
        # )
        self.login_button_image = ImageTk.PhotoImage(Images.login_button_png)
        # self.login_hover_button = tk.PhotoImage(
        #     file=getImages("login_signup_screen/login_hover_button.png")
        # )
        self.login_hover_button = ImageTk.PhotoImage(Images.login_hover_button_png)
        self.login_button = tk.Button(
            self,
            image=self.login_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: startThread(lambda: asyncio.run(self.onLogin()), "login", True),
            relief="flat",
            bd=0,
        )
        self.login_button.place(x=129.0, y=341.0, width=224.0, height=55.0)

        self.login_button.bind("<Enter>", self.loginButtonHover)
        self.login_button.bind("<Leave>", self.loginButtonLeave)

        self.canvas.create_rectangle(
            0.0, 309.0, 475.0, 310.0, fill="#101520", outline=""
        )
        self.canvas.create_text(
            210.0,
            104.0,
            anchor="nw",
            text=renderBiDiText("اسم المستخدم") if arabic else "username",
            fill="#7D88A7",
            font=("Arial", 12 * -1),
        )

        self.canvas.create_text(
            215.0,
            180.0,
            anchor="nw",
            text=renderBiDiText("كلمة السر") if arabic else "password",
            fill="#7D88A7",
            font=("Arial", 12 * -1),
            justify="center",
        )
        self.canvas.create_text(
            207.0 if arabic else 169.0,
            262.0,
            anchor="nw",
            text=(
                renderBiDiText("لا تملك حساب؟") if arabic else "don’t have an account?"
            ),
            fill="#FFFFFF",
            font=("Arial", 12 * -1),
        )

        # self.login_signup_button_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/login_signup_button.png")
        # )
        # self.login_signup_hover_button_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/login_signup_hover_button.png")
        # )
        self.login_signup_button = tk.Button(
            self,
            image=self.login_signup_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.master.show_frame("SignupPage"),
            relief="flat",
        )
        self.login_signup_button.place(x=202.0, y=281.0, width=69.0, height=15.0)

        self.login_signup_button.bind("<Enter>", self.loginSignupButtonHover)
        self.login_signup_button.bind("<Leave>", self.loginSignupButtonLeave)

        # self.login_username_entry_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/login_entry_1.png")
        # )

        self.canvas.create_image(246.0, 140.0, image=self.login_username_entry_image)

        self.login_username_entry = tk.Entry(
            self, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0
        )

        self.login_username_entry.place(x=131.0, y=121.0, width=230.0, height=36.0)

        self.login_username_entry.bind("<KeyRelease>", self.loginUsernameChecker)

        # self.login_password_entry_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/login_entry_2.png")
        # )

        self.canvas.create_image(246.5, 220.0, image=self.login_password_entry_image)

        self.login_password_entry = tk.Entry(
            self, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, show="*"
        )
        self.login_password_entry.place(x=131.0, y=201.0, width=230.0, height=36.0)

        # self.entry_bg_icon_image_1 = tk.PhotoImage(
        #     file=getImages("login_signup_screen/entry_bg_icon_image_1.png")
        # )

        self.canvas.create_image(119.0, 220.0, image=self.entry_bg_icon_image_1)

        # self.entry_bg_icon_image_2 = tk.PhotoImage(
        #     file=getImages("login_signup_screen/entry_bg_icon_image_2.png")
        # )

        self.canvas.create_image(119.0, 140.0, image=self.entry_bg_icon_image_2)

        # self.username_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/username_icon.png")
        # )

        self.canvas.create_image(116.0465087890625, 139.0, image=self.username_icon)

        # self.password_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/password_icon.png")
        # )

        self.canvas.create_image(118.02114868164062, 219.0, image=self.password_icon)

        self.login_button.bind(
            "<Button-1>", lambda _: [self.login_button.invoke(), "break"][-1], add=True
        )
        self.login_signup_button.bind(
            "<Button-1>",
            lambda _: [self.login_signup_button.invoke(), "break"][-1],
            add=True,
        )

    async def onLogin(self):

        if self.master.current_frame != "LoginPage": 
            return
        if self.running: 
            return

        self.running = True

        loading = AnimatedGIF(self, Images.loading_gif, "#38446A", 350, 295)

        sleep(2)

        if not self.valid_username:
            messagebox.showerror(
                "invalid username",
                (
                    renderBiDiText("اسم المستخدم غير مدعوم")
                    if arabic
                    else "username is invalid"
                ),
            )
            loading.clear_canvas()
            return

        if not self.login_password_entry.get():
            messagebox.showerror(
                "invalid password",
                (
                    renderBiDiText("ضع كلمة السر")
                    if arabic
                    else "a password is required"
                ),
            )
            loading.clear_canvas()
            return

        try:
            response = await API().login(
                self.login_username_entry.get(),
                self.login_password_entry.get(),
                UserCredentials().serial.crossSystemSerial,
            )

            if response == "invalid credentials":
                messagebox.showerror(
                    "invalid credentials",
                    (
                        renderBiDiText("اسم المستخدم او كلمة السر غير صحيح")
                        if arabic
                        else "username or password is wrong"
                    ),
                )
            elif response == "please check you email to confirm your login":
                messagebox.showerror(
                    "confirm login",
                    (
                        renderBiDiText("يرجى التحقق من تسجيل الدخول، تفقد الإيميل")
                        if arabic
                        else "please check your email inbox for a verification link"
                    ),
                )
            elif response == "please authenticate your account first":
                if messagebox.askyesno(
                    "authentication",
                    (
                        renderBiDiText(
                            "يرجى توثيق الحساب، تفقد الإيميل\n\n\n،هل تريد اعادة ارسال التحقق"
                        )
                        if arabic
                        else "please authenticate you account first, check you email inbox for a link\n\n would you like to send the link again?"
                    ),
                ):
                    response = await API().resendAccountVerify(
                        self.login_username_entry.get(), self.login_password_entry.get()
                    )
            elif response == "success":
                messagebox.showinfo(
                    "success",
                    (
                        renderBiDiText("تم تسجيل الدخول")
                        if arabic
                        else "login successfull"
                    ),
                )
                self.master.withdraw()
                self.master.quit()
                self.master.destroy()
                self.master.unbind_all("<Any-KeyPress>")
                self.master.unbind_all("<Any-ButtonPress>")

            else:
                messagebox.showerror(
                    "error",
                    (
                        renderBiDiText("مشكله غير معروفه، يرجى المحاوله لاحقا")
                        if arabic
                        else "unknwon error, please try again"
                    ),
                )

        except Exception as e:
            logger.error(f"An error occurred in the login, error: {e}, error stack: {getStack()}")
            messagebox.showerror(
                "server error",
                (
                    renderBiDiText("مشكله غير معروفه، يرجى المحاوله لاحقا")
                    if arabic
                    else "something went wrong, please try again later"
                ),
            )

        loading.clear_canvas()
        self.running = False

    def loginUsernameChecker(self, e):
        if re.fullmatch(
            r"^[a-z0-9\-_]{5,}$",
            self.login_username_entry.get(),
        ):
            self.valid_username = True
        else:
            self.valid_username = False

    def loginButtonHover(self, e):
        self.login_button.config(image=self.login_hover_button)

    def loginButtonLeave(self, e):
        self.login_button.config(image=self.login_button_image)

    def loginSignupButtonHover(self, e):
        self.login_signup_button.config(image=self.login_signup_hover_button_image)

    def loginSignupButtonLeave(self, e):
        self.login_signup_button.config(image=self.login_signup_button_image)


class SignupPage(tk.Frame):
    def __init__(self, parent, master):
        super().__init__(parent)
        self.valid_email = False
        self.valid_password = False
        self.valid_username = False
        self.running = False
        self.master = master

        self.canvas = tk.Canvas(
            self,
            bg="#101520",
            height=418,
            width=467,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        self.canvas.place(x=0, y=0)

        # self.signup_background = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_background.png")
        # )
        self.signup_background = ImageTk.PhotoImage(Images.signup_background_png)
        self.signup_button_image = ImageTk.PhotoImage(Images.signup_button_png)
        self.signup_hover_button_image = ImageTk.PhotoImage(
            Images.signup_hover_button_png
        )
        self.signup_login_button_image = ImageTk.PhotoImage(
            Images.signup_login_button_png
        )
        self.signup_login_hover_button_image = ImageTk.PhotoImage(
            Images.signup_login_hover_button_png
        )
        self.signup_username_entry_image = ImageTk.PhotoImage(Images.signup_entry_2_png)
        self.signup_email_entry_image = ImageTk.PhotoImage(Images.signup_entry_1_png)
        self.signup_password_entry_image = ImageTk.PhotoImage(Images.signup_entry_3_png)
        self.signup_entry_1_bg_icon = ImageTk.PhotoImage(
            Images.signup_entry_1_bg_icon_png
        )
        self.signup_entry_2_bg_icon = ImageTk.PhotoImage(
            Images.signup_entry_2_bg_icon_png
        )
        self.signup_entry_3_bg_icon = ImageTk.PhotoImage(
            Images.signup_entry_3_bg_icon_png
        )
        self.signup_username_icon = ImageTk.PhotoImage(Images.username_icon_png)
        self.signup_email_icon = ImageTk.PhotoImage(Images.email_icon_png)
        self.signup_password_icon = ImageTk.PhotoImage(Images.password_icon_png)

        self.canvas.create_image(238.0, 209.0, image=self.signup_background)

        self.username_circle = Circle(self.canvas, "#060A17", (80, 100))
        self.email_circle = Circle(self.canvas, "#060A17", (80, 170))
        self.password_circle = Circle(self.canvas, "#060A17", (80, 240))

        self.canvas.create_text(
            175.0 if arabic else 132.0,
            13.0,
            anchor="nw",
            text=renderBiDiText("إنشاء حساب") if arabic else "Create an account",
            fill="#FFFFFF",
            font=("Arial", 24 * -1),
        )

        # self.signup_button_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_button.png")
        # )
        # self.signup_hover_button_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_hover_button.png")
        # )
        self.signup_button = tk.Button(
            self,
            image=self.signup_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: startThread(lambda: self.on_signup(), "signup", True),
            relief="flat",
        )
        self.signup_button.place(x=129.0, y=341.0, width=224.0, height=55.0)

        self.canvas.create_rectangle(0.0, 309.0, 475.0, 310.0, fill="#101520")

        self.canvas.create_text(
            205 if arabic else 201.0,
            63.0,
            anchor="nw",
            text=renderBiDiText("اسم المستخدم") if arabic else "username",
            fill="#7D88A7",
            font=("Arial", 12 * -1),
        )

        self.canvas.create_text(
            217.0 if arabic else 214.0,
            134.0,
            anchor="nw",
            text=renderBiDiText("الإيميل") if arabic else "email",
            fill="#7D88A7",
            font=("Arial", 12 * -1),
        )

        self.canvas.create_text(
            213.0 if arabic else 205.0,
            205.0,
            anchor="nw",
            text=renderBiDiText("كلمه السر") if arabic else "password",
            fill="#7E88A8",
            font=("Arial", 12 * -1),
        )
        self.canvas.create_text(
            210.0 if arabic else 167.0,
            268.0,
            anchor="nw",
            text=renderBiDiText("لديك حساب؟") if arabic else "already have an account?",
            fill="#FFFFFF",
            font=("Arial", 12 * -1),
        )

        # self.signup_login_button_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_login_button.png")
        # )
        # self.signup_login_hover_button_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_login_hover_button.png")
        # )
        self.signup_login_button = tk.Button(
            self,
            image=self.signup_login_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.master.show_frame("LoginPage"),
            relief="flat",
        )
        self.signup_login_button.place(x=202.0, y=287.0, width=69.0, height=15.0)

        # self.signup_username_entry_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_entry_2.png")
        # )

        self.canvas.create_image(246.0, 99.0, image=self.signup_username_entry_image)

        self.signup_username_entry = tk.Entry(
            self, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0
        )
        self.signup_username_entry.place(x=131.0, y=80.0, width=230.0, height=36.0)

        # self.signup_email_entry_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_entry_1.png")
        # )

        self.canvas.create_image(246.0, 170.0, image=self.signup_email_entry_image)

        self.signup_email_entry = tk.Entry(
            self, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0
        )
        self.signup_email_entry.place(x=131.0, y=151.0, width=230.0, height=36.0)

        # self.signup_password_entry_image = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_entry_3.png")
        # )

        self.canvas.create_image(246.0, 241.0, image=self.signup_password_entry_image)

        self.signup_password_entry = tk.Entry(
            self, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, show="*"
        )
        self.signup_password_entry.place(x=131.0, y=222.0, width=230.0, height=36.0)

        # self.signup_entry_1_bg_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_entry_1_bg_icon.png")
        # )

        self.canvas.create_image(119.0, 241.0, image=self.signup_entry_1_bg_icon)

        # self.signup_entry_2_bg_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_entry_2_bg_icon.png")
        # )

        self.canvas.create_image(119.0, 170.0, image=self.signup_entry_2_bg_icon)

        # self.signup_entry_3_bg_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/signup_entry_3_bg_icon.png")
        # )

        self.canvas.create_image(119.0, 99.0, image=self.signup_entry_3_bg_icon)

        # self.signup_username_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/username_icon.png")
        # )

        self.canvas.create_image(
            116.0465087890625, 98.0, image=self.signup_username_icon
        )

        # self.signup_email_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/email_icon.png")
        # )

        self.canvas.create_image(118.0, 169.0, image=self.signup_email_icon)

        # self.signup_password_icon = tk.PhotoImage(
        #     file=getImages("login_signup_screen/password_icon.png")
        # )

        self.canvas.create_image(
            118.02114868164062, 240.0, image=self.signup_password_icon
        )

        self.signup_button.bind("<Enter>", self.signupButtonHover)
        self.signup_button.bind("<Leave>", self.signupButtonLeave)

        self.signup_login_button.bind("<Enter>", self.signupLoginButtonHover)
        self.signup_login_button.bind("<Leave>", self.signupLoginButtonLeave)

        self.signup_email_entry.bind("<KeyRelease>", self.signupEmailRegex)
        self.signup_username_entry.bind("<KeyRelease>", self.signupUsernameRegex)
        self.signup_password_entry.bind("<KeyRelease>", self.signupPasswordRegex)
        self.signup_button.bind(
            "<Button-1>", lambda _: [self.signup_button.invoke(), "break"][-1], add=True
        )
        self.signup_login_button.bind(
            "<Button-1>",
            lambda _: [self.signup_login_button.invoke(), "break"][-1],
            add=True,
        )

    def on_signup(self):

        if self.master.current_frame != "SignupPage": 
            return
        if self.running: 
            return

        # loading = AnimatedGIF(
        #     self, getImages("login_signup_screen/loading.gif"), "#060A17", 350, 300
        # )
        self.running = True
        loading = AnimatedGIF(self, Images.loading_gif, "#060A17", 350, 300)
        sleep(2)
        if self.valid_email and self.valid_password and self.valid_username:

            respone = API().createAccount(
                self.signup_username_entry.get(),
                self.signup_email_entry.get(),
                self.signup_password_entry.get(),
                UserCredentials().user,
                UserCredentials().serial.crossSystemSerial,
                UserCredentials().ip.get("ip"),
                UserCredentials().ip.get("region"),
            )

            if respone == "email is used for another account":
                messagebox.showerror(
                    "used email",
                    (
                        renderBiDiText(
                            f"مستخدم في حساب اخر\n\n{self.signup_email_entry.get()}"
                        )
                        if arabic
                        else f"{self.signup_email_entry.get()} is used for another account"
                    ),
                )
            elif respone == "malformed email":
                messagebox.showerror(
                    "incorrect email",
                    (
                        renderBiDiText("إيميل غير مدعوم")
                        if arabic
                        else "please use a correct email"
                    ),
                )
            elif respone == "malformed username":
                messagebox.showerror(
                    "incorrect username",
                    (
                        renderBiDiText("اسم مستخدم غير مدعوم")
                        if arabic
                        else "please use a correct username"
                    ),
                )
            elif respone == "username is already reserved":
                messagebox.showerror(
                    "used username",
                    (
                        renderBiDiText(
                            f"مستخدم في حساب اخر\n\n{self.signup_email_entry.get()}"
                        )
                        if arabic
                        else f"{self.signup_username_entry.get()} is used for another account"
                    ),
                )
            elif respone == "You cannot create any more accounts":
                messagebox.showerror(
                    "no more account",
                    (
                        renderBiDiText(
                            "لا يمكنك إنشاء حسابات أكثر من واحد \n\nيرجى التواصل بي إذا كنت تعتقد أن هذا خطأ"
                        )
                        if arabic
                        else "you can't create accounts more than 1 \n\nplease contact me if you think this is wrong"
                    ),
                )
            elif respone == "success":
                self.master.show_frame("LoginPage")
                messagebox.showinfo(
                    "success",
                    (
                        renderBiDiText("تم إنشاء الحساب بنجاح، تفقد الإيميل")
                        if arabic
                        else "account created successfully, please check your inbox"
                    ),
                )
        else:
            messagebox.showerror(
                "invalid signup",
                (
                    renderBiDiText("يرجى وضع بيانات صحيحه")
                    if arabic
                    else "please put a correct credentials"
                ),
            )

        self.running = False
        loading.clear_canvas()

    def signupButtonHover(self, e):
        self.signup_button.config(image=self.signup_hover_button_image)

    def signupButtonLeave(self, e):
        self.signup_button.config(image=self.signup_button_image)

    def signupLoginButtonHover(self, e):
        self.signup_login_button.config(image=self.signup_login_hover_button_image)

    def signupLoginButtonLeave(self, e):
        self.signup_login_button.config(image=self.signup_login_button_image)

    def signupEmailRegex(self, e):
        if re.fullmatch(
            r"^(?:[a-zA-Z0-9_-]+(?:(?:\.[a-zA-Z0-9_-]+)*))@(?P<domain_part>(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]{2,}(?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)$",
            self.signup_email_entry.get(),
        ):
            self.email_circle.set_color("#29aa00")
            self.valid_email = True
        else:
            self.email_circle.set_color("#900000")
            self.valid_email = False

    def signupUsernameRegex(self, e):
        if re.fullmatch(r"[a-z0-9\-_]{5,}", self.signup_username_entry.get()):
            self.username_circle.set_color("#29aa00")
            self.valid_username = True
        else:
            self.username_circle.set_color("#900000")
            self.valid_username = False

    def signupPasswordRegex(self, e):
        if re.fullmatch(
            r"[a-zA-Z0-9!@#$%^&*()_\-?';~`:,\[\]\{\}]{5,}",
            self.signup_password_entry.get(),
        ):
            self.password_circle.set_color("#29aa00")
            self.valid_password = True
        else:
            self.password_circle.set_color("#900000")
            self.valid_password = False


class App(tk.Toplevel):
    def __init__(self, page_to_show):
        super().__init__()
        self.title("Login and Signup")
        self.geometry("467x418")
        self.resizable(False, False)
        self.focus()
        self.current_frame = None
        icon = ImageTk.PhotoImage(
                Images.YemenIPCC_png,
                master=self,
            )

        self.iconphoto(True, icon)
        self.protocol(
            "WM_DELETE_WINDOW",
            lambda: [self.withdraw(), self.destroy(), handleExit()],
        )

        # Center the window
        self.center_window(467, 418)

        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")

        self.login_page = LoginPage(parent=self.container, master=self)
        self.signup_page = SignupPage(parent=self.container, master=self)

        self.frames = {"LoginPage": self.login_page, "SignupPage": self.signup_page}

        self.bind(
            "<Return>",
            lambda n: [
                self.login_page.login_button.invoke(),
                self.signup_page.signup_button.invoke(),
            ],
        )

        self.show_frame(page_to_show)

    def center_window(self, width, height):
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position x, y
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)

        # Set window position
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.pack(fill="both", expand=True)
        frame.tkraise()
        for other_frame in self.frames.values():
            if other_frame != frame:
                other_frame.pack_forget()
        self.current_frame = page_name


def main_(page_to_show: Literal["SignupPage", "LoginPage"]):
    # startThread(lambda: App(page_to_show).mainloop(), "Login/Signup Screen", True)
    App(page_to_show).mainloop()


# main_()
