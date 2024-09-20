import os
import ctypes


from .get_app_dir import getAppDirectory

from .get_system import system

font_path = os.path.join(getAppDirectory(), "resources", "font", "almarai.ttf")


def setWindowsFont():
    ctypes.windll.gdi32.AddFontResourceW(rf"{font_path}")


def setFont():
    match system:
        case "Windows":
            setWindowsFont()
        case "Mac":
            ...
        case "Linux":
            ...


def getFont() -> str:
    match system:
        case "Windows":
            return "Almarai"
        case "Mac":
            return "SF Pro"
        case "Linux":
            return "Arial"
