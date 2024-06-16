# Its purpose is just to keep the main script cleaner

import subprocess
import tkinter as tk
from tkinter import messagebox, font
from tkinter.ttk import Progressbar
from tempfile import gettempdir, TemporaryDirectory
import os 
from time import sleep 
from threading import Thread, Event
from typing import Dict, List, Any, Union, Tuple, Callable, Optional
import socket
import platform
import requests
import webbrowser
import sys
import shutil
from functools import cache
import ctypes
from pathlib import Path
import argparse
import logging
import aiohttp
import asyncio
import textwrap
from contextlib import contextmanager

from .updating_status import DPIResize, DeviceManager
from .logging_config import logging



dsystem = platform.system()

# Used to change the "Darwin" to "Mac" because it is known better in Mac not Darwin
if dsystem == "Darwin":
    system: str = "Mac"
else:
    system = dsystem

# Reused functions:

@contextmanager
def managedProcess(*args, **kwargs):
    process = subprocess.Popen(*args, **kwargs)
    try:
        yield process
    except Exception as e:
        logging.error(f"updating_status.py - An error occurred in the managedProcess, error: {e}")
    finally:
        process.terminate()
        process.wait()

def getAppDirectory() -> str:
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    if bundle_dir.endswith("Scripts"):
        bundle_dir = bundle_dir[:-len("Scripts")]
    
    return bundle_dir

def getDefaultFont():
    system = platform.system()
    
    if system == "Windows":
        return "Segoe UI"
    elif system == "Darwin":  # macOS
        return "SF Pro"
    elif system == "Linux":
        return getLinuxDefaultFont()
    else:
        return "Sans"  # Default to a generic font if OS is not recognized

def getLinuxDefaultFont():
    # Define processes commonly associated with each DE
    de_processes = {
        "gnome": ["gnome-shell", "gnome-session"],
        "kde": ["plasmashell", "kwin_x11"],
        "xfce": ["xfce4-session"],
        "lxde": ["lxsession"],
        "mate": ["mate-session"],
        "cinnamon": ["cinnamon-session"],
        "unity": ["unity-panel-service"],
        "deepin": ["dde-session-daemon"],
        "pantheon": ["gala", "wingpanel"],
        "budgie": ["budgie-wm"],
        "i3": ["i3"],
        "sway": ["sway"],
        "enlightenment": ["enlightenment"]
    }

    try:
        # Get the list of running processes
        with managedProcess(["ps", "-e", "-o", "comm="], stdout=subprocess.PIPE) as process:
            stdout, _ = process.communicate()
            running_processes = stdout.decode().splitlines()

        # Check for known processes
        for de, processes in de_processes.items():
            for p in processes:
                if p in running_processes:
                    if de == "gnome":
                        return "Cantarell"
                    elif de == "kde":
                        return "Oxygen"
                    elif de == "xfce":
                        return "DejaVu Sans"
                    elif de == "lxde":
                        return "Liberation Sans"
                    elif de == "mate":
                        return "Ubuntu"
                    elif de == "cinnamon":
                        return "Noto Sans"
                    elif de == "unity":
                        return "Ubuntu"
                    elif de == "deepin":
                        return "Noto Sans"
                    elif de == "pantheon":
                        return "Open Sans"
                    elif de == "budgie":
                        return "Noto Sans"
                    elif de == "i3":
                        return "DejaVu Sans"
                    elif de == "sway":
                        return "DejaVu Sans"
                    elif de == "enlightenment":
                        return "Noto Sans"
        return "Sans"  # Default to a generic font if DE is not recognized
    except Exception as e:
        print("Error:", e)
        return "Sans"  # Default to a generic font in case of any error
    
family_font = getDefaultFont()



# Long Variables:

new_iPhone_message = f"""You should have a Verizon sim, if you don't, this won't work!
                            
                            
1. Make sure there is no sim inside your device 

2. Let the app inject the file

3. Reboot the device

4. Put your Verizon sim

5. Now swap it with the YemenMobile sim

6. Make an emergency call to 911

7. Swap the sim to Verizon

8. Make an emergency call to 911 (you should get the sim indicator working)

9. Do a force reboot (Volume up then down and keep pressing the power button until the Apple logo appear)

10. Swap the sim to YemenMobile


After that, everything should work.


⚠️NOTE: if that is not working, you have to repeat until you get it to work!"""


new_iPhones = ["iPhone 12 Mini", "iPhone 12", "iPhone 12 Pro", "iPhone 12 Pro Max",
               "iPhone 13 Mini", "iPhone 13", "iPhone 13 Pro", "iPhone 13 Pro Max"]