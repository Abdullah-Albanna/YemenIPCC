# For relative imports to work in Python 3.6
# import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# bundle_dir = (sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath('.'))

import sys
from .utils.get_system import system
from pathlib import Path

moduel_path = str(Path(__file__).parent)

if moduel_path not in sys.path:
    sys.path.append(moduel_path)

if system == "Mac":
    # Only import the Button from ttwidgets if it is a mac, tk's button for macs look bad
    from ttwidgets.ttwidgets import Button  # type: ignore
else:
    from tkinter import Button
