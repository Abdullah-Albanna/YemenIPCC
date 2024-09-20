import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import math

from ..utils.images import Images

from ..thread_managment.thread_terminator_var import terminate_splash_screen

class SplashScreen(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.show_splash()

    def show_splash(self):
        self.title("Splash Screen")
        self.overrideredirect(1)
        self.attributes("-topmost", True)

        width_of_window = 427
        height_of_window = 250
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_coordinate = (screen_width // 2) - (width_of_window // 2)
        y_coordinate = (screen_height // 2) - (height_of_window // 2)
        self.geometry(
            f"{width_of_window}x{height_of_window}+{x_coordinate}+{y_coordinate}"
        )

        self.canvas = tk.Canvas(
            self, width=427, height=250, bg="#030B2C", highlightthickness=0
        )
        self.canvas.pack()

        self.set_background_image()

        self.ring = self.canvas.create_oval(
            154, 62, 274, 175, outline="#040C2C", width=10
        )

        self.load_image()

        self.start_color = "#040C2C"  # Darker color
        self.end_color = "#364BA1"  # Brighter color
        self.transition_steps = 150
        self.step = 0
        self.direction = 1  # 1 for brightening, -1 for darkening
        self.glow()
        self.validate_exit()

    def set_background_image(self):
        bg_image = Images.background_png
        bg_image = bg_image.resize((427, 250), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_image)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

    def load_image(self):
        image = Images.YemenIPCC_png
        image = image.resize((120, 116), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)

        mask = Image.new("L", (120, 116), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 120, 116), fill=255)

        circular_image = Image.new("RGBA", (120, 116))
        circular_image.paste(image, (0, 0), mask=mask)
        self.photo = ImageTk.PhotoImage(circular_image)

        self.canvas.create_image(214, 119, image=self.photo, anchor="center")

    def interpolate_color(self, start_color, end_color, t):

        start_color = [int(start_color[i : i + 2], 16) for i in (1, 3, 5)]
        end_color = [int(end_color[i : i + 2], 16) for i in (1, 3, 5)]

        r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * t)

        return f"#{r:02x}{g:02x}{b:02x}"

    def ease_in_out(self, t):
        return 0.5 * (1 - math.cos(math.pi * t))

    def glow(self):

        t = (self.step % self.transition_steps) / self.transition_steps
        eased_t = self.ease_in_out(t)

        color = self.interpolate_color(self.start_color, self.end_color, eased_t)

        self.canvas.itemconfig(self.ring, outline=color)

        # Update the step and direction
        if self.direction == 1:  # Brightening
            self.step += 1
            if self.step >= self.transition_steps:
                self.direction = -1
        else:  # Darkening
            self.step -= 1
            if self.step <= 0:
                self.direction = 1

        self.after(10, self.glow)

    def validate_exit(self):
        if terminate_splash_screen.is_set():
            self.withdraw()
            self.destroy()
        else:
            self.after(50, self.validate_exit)


def splash():
    splash = SplashScreen()
    splash.after(1000, splash.quit)
    splash.mainloop()
