import tkinter as tk
from tkinter import PhotoImage
from ..utils.get_images import getImages

class WorkFlow(tk.Canvas):
    def __init__(self, master):
        super().__init__(master)
        
        raise NotImplementedError

        # self.configure(
        #     bg="#FFFFFF",
        #     height=100,
        #     width=500,
        #     bd=0,
        #     highlightthickness=0,
        #     relief="ridge"
        # )

        # self.place(x=0, y=0)

        # # Store the PhotoImage object as an instance attribute to prevent garbage collection
        # self.image_image_1 = PhotoImage(file=getImages("workflow/choose_bundle.png"))
        # self.create_image(
        #     100.0,
        #     100.0,
        #     image=self.image_image_1
        # )

        # self.place(relx=0.5, rely=0.5)