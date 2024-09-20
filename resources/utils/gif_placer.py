import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO

class AnimatedGIF:
    def __init__(self, parent, gif: BytesIO, color, width=None, height=None, x=0, y=0):
        self.parent = parent
        self.gif = gif
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.frames = self.extract_frames()
        self.frame_index = 0

        # Initialize Canvas
        self.canvas = tk.Canvas(parent, bg=color, highlightthickness=0)
        self.update_canvas_size()
        self.canvas.pack()

        # Initially hide the canvas and show it after a short delay to avoid glitch
        self.canvas.pack_forget()
        self.parent.after(0, self.show_canvas)  # Delay to avoid initial glitch

        # Start animation
        self.animate()

    # def extract_frames(self):
    #     frames = []
    #     durations = []
    #     # with Image.open(self.gif_path) as img:
    #     original_width, original_height = self.gif.size
    #     if self.width and self.height:
    #         new_size = (int(self.width), int(self.height))
    #     else:
    #         new_size = (original_width, original_height)

    #     try:
    #         while True:
    #             # Convert to RGBA to handle transparency and resize
    #             frame = self.gif.convert("RGBA").resize(new_size, Image.LANCZOS)
    #             frame_tk = ImageTk.PhotoImage(frame)
    #             frames.append(frame_tk)
    #             durations.append(
    #                 self.gif.info.get("duration", 100)
    #             )  # Default duration to 100 ms
    #             self.gif.seek(self.gif.tell() + 1)
    #     except EOFError:
    #         pass
    #     self.gif.close()
    #     self.durations = durations
    #     return frames

    def extract_frames(self):
        frames = []
        durations = []
        with Image.open(self.gif) as img:
            original_width, original_height = img.size
            if self.width and self.height:
                new_size = (int(self.width), int(self.height))
            else:
                new_size = (original_width, original_height)

            try:
                while True:
                    # Convert to RGBA to handle transparency and resize
                    frame = img.convert("RGBA").resize(new_size, Image.LANCZOS)
                    frame_tk = ImageTk.PhotoImage(frame)
                    frames.append(frame_tk)
                    durations.append(
                        img.info.get("duration", 100)
                    )  # Default duration to 100 ms
                    img.seek(img.tell() + 1)
            except EOFError:
                pass
        self.durations = durations
        return frames

    def update_canvas_size(self):
        # Set Canvas size to the desired dimensions based on GIF size
        if self.frames:
            self.canvas.config(
                width=self.frames[0].width(), height=self.frames[0].height()
            )

    def show_canvas(self):
        self.canvas.pack(pady=10, padx=10)  # Adjust padding if needed

    def animate(self):
        if self.frames:
            self.canvas.delete("all")
            frame = self.frames[self.frame_index]
            self.canvas.create_image(self.x, self.y, image=frame, anchor=tk.NW)
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            # Use frame duration to control animation speed
            self.parent.after(self.durations[self.frame_index], self.animate)

    def clear_canvas(self):
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.delete("all")
            self.canvas.pack_forget()