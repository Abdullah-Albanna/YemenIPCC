from . import (
    tk, 
    logger,
    cache
)

from .get_system import system



@cache
def cachedDPIAndRes() -> tuple[float | int]:
    """
    Caches the dpi and the screen resolution and returns them
    """

    checked_the_dpi = False
    window = tk.Tk()
    dpi = window.winfo_fpixels('1i')
    if not checked_the_dpi:
        logger.info(f"DPI: {round(dpi)}")
        checked_the_dpi = True
    screen_width = window.winfo_screenwidth()
    window.destroy()
    return dpi, screen_width

def DPIResize(size) -> int:
    """
    Get the screen DPI and screen resolution using Tkinter, and convert the font size to be suitable for it
    """

    if system == "Mac":
        # Macs are known to use 72
        sysdpi = 72

    else:
        sysdpi = 96

    dpi, screen_width = cachedDPIAndRes()

    if 1366 <= screen_width < 1600:
        sysdpi+=9

    elif 1280 <= screen_width < 1366:
        sysdpi+=10

    elif 1024 <= screen_width < 1280:
        sysdpi+=2

    scale_factor = dpi / sysdpi

    return round(int(size * scale_factor))