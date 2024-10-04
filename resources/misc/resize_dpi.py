import tkinter as tk
from functools import cache


from utils.logger_config_class import YemenIPCCLogger
from utils.get_system import system

logger = YemenIPCCLogger().logger


@cache
def cachedDPIAndResolution() -> tuple[float, int, int]:
    """
    Caches the DPI and the screen resolution and returns them.
    """
    window = tk.Tk()
    dpi = window.winfo_fpixels("1i")
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.destroy()
    logger.info(f"DPI: {round(dpi)}")
    return dpi, screen_width, screen_height


def DPIResize(base_size: int) -> int:
    """
    Get the screen DPI and screen resolution using Tkinter,
    and convert the font size to be suitable for it.
    """
    if system == "Mac":
        sys_dpi = 60  # Macs typically use 72 DPI
    else:
        sys_dpi = 96  # Default for other systems

    dpi, screen_width, screen_height = cachedDPIAndResolution()

    # Adjust sys_dpi based on screen width
    if 1366 <= screen_width < 1600:
        sys_dpi += 5
    elif 1280 <= screen_width < 1366:
        sys_dpi += 10
    elif 1024 <= screen_width < 1280:
        sys_dpi += 2

    # Calculate scale factor based on DPI
    dpi_scale_factor = dpi / sys_dpi

    # Calculate scale factor based on screen dimensions
    screen_scale_factor = (screen_width / 1920 + screen_height / 1080) / 2

    # Combine both scale factors
    combined_scale_factor = dpi_scale_factor * screen_scale_factor

    # Adjust the base font size by the combined scale factor
    return round(base_size * combined_scale_factor)
