

from .get_system import system
from .byte_objects import almarai_font

win_font_name = None

def setWindowsFont():
    global win_font_name

    import ctypes
    from ctypes import wintypes
    import base64

    font_bytes = base64.b64decode(almarai_font)
    font_buffer = ctypes.create_string_buffer(font_bytes)

    gdi32 = ctypes.WinDLL("gdi32")
    AddFontMemResourceEx = gdi32.AddFontMemResourceEx
    AddFontMemResourceEx.argtypes = [wintypes.LPCVOID, wintypes.DWORD, wintypes.LPVOID, ctypes.POINTER(wintypes.DWORD)]
    AddFontMemResourceEx.restype = wintypes.DWORD

    num_fonts = wintypes.DWORD(0)
    if AddFontMemResourceEx(font_buffer, len(font_bytes), None, ctypes.byref(num_fonts)) != 0:
        win_font_name = "Almarai"

    # ctypes.windll.gdi32.AddFontResourceW(rf"{font_path}")


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
            return win_font_name if win_font_name is not None else "Segoe UI"
        case "Mac":
            return "SF Pro"
        case "Linux":
            return "Arial"