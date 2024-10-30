from tkinter import messagebox, Toplevel


class MessageBox:
    """
    Used for topmost message boxes, to make the message box always on top
    """
    def __init__(self):
        self.top = Toplevel()
        self.top.withdraw()  # Hide the Toplevel window itself

        # Set the Toplevel window as always on top
        self.top.attributes("-topmost", True)

        self.top.grab_set()

    def showinfo(self, title: str | None = None, message: str | None = None):
        return messagebox.showinfo(title, message)

    def showwarning(self, title: str | None = None, message: str | None = None):
        return messagebox.showwarning(title, message)

    def showerror(self, title: str | None = None, message: str | None = None):
        return messagebox.showerror(title, message)

    def askquestion(self, title: str | None = None, message: str | None = None):
        return messagebox.askquestion(title, message)

    def askokcancel(self, title: str | None = None, message: str | None = None):
        return messagebox.askokcancel(title, message)

    def askyesno(self, title: str | None = None, message: str | None = None):
        return messagebox.askyesno(title, message)

    def askyesnocancel(self, title: str | None = None, message: str | None = None):
        return messagebox.askyesnocancel(title, message)

    def askretrycancel(self, title: str | None = None, message: str | None = None):
        return messagebox.askretrycancel(title, message)
