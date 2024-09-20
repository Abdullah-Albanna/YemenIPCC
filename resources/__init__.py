
# For relative imports to work in Python 3.6
#import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# bundle_dir = (sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath('.')) 

## This was replaced later on, and got deleted, it was used for pyinstaller, but migrated to nuitka,  just leaving it here, because why not! :)
# __version__ = 
# from loguru import logger
# import subprocess
# import tkinter as tk
# from tkinter import messagebox, font, filedialog
# from tkinter.ttk import Progressbar, Style
# from tempfile import gettempdir, TemporaryDirectory
# import os 
# from time import sleep 
# from threading import Thread, Event
# from typing import Dict, List, Any, Union, Tuple, Annotated, Optional, Literal
# import socket
# import platform
# import requests
# import webbrowser
# import sys
# from functools import cache, lru_cache
# from pathlib import Path
# import argparse
# import aiohttp
# import asyncio
# import textwrap
# import glob
# import re
# import uuid
# import signal
# from datetime import datetime
# import ctypes 
# from itertools import islice, count
from .utils.get_system import system
# from pydantic_settings import BaseSettings
# from pydantic import Field
# import keyring
# import json
# import tinydb
# from tinydb.storages import JSONStorage
# from PIL import Image, ImageTk, ImageDraw
# from contextlib import contextmanager
# import getpass
# import psutil
# import ssl
# import stat
# import certifi
# import math
# import tkthread

if system == "Mac":
    # Only import the Button from ttwidgets if it is a mac, tk's button for macs look bad
    from ttwidgets.ttwidgets import Button # type: ignore
else:
    from tkinter import Button

# if system == "Windows":
#     import win32console  # type: ignore

# Long Variables:

# This is the message that appears if a connected iPhone is in 12 - 13 PM
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

arabic_new_iphone_message = f"""يجب أن يكون لديك شريحة فرايزون إذا لم تكن لديك، فلن يعمل هذا!

1. تأكد من عدم وجود شريحة في جهازك

2. دع التطبيق يقوم بحقن الملف

3. أعد تشغيل الجهاز

4. ضع شريحة فرايزون 

5. الآن قم بتبديلها بشريحة يمن موبايل

6. قم بإجراء مكالمة طوارئ إلى 911

7. قم بتبديل الشريحة إلى فرايزون 

8. قم بإجراء مكالمة طوارئ إلى 911 (يجب أن يظهر مؤشر الشريحة)

9. قم بإعادة التشغيل بالقوة (اضغط على زر رفع الصوت ثم خفضه واستمر في الضغط على زر الطاقة حتى يظهر شعار ابل)

10. قم بتبديل الشريحة إلى يمن موبايل 

بعد ذلك، يجب أن يعمل كل شيء

ملاحظة: إذا لم يعمل ذلك، يجب عليك تكرار العملية حتى تنجح!⚠️"""



# A list of the iPhone version that requires a special treatment
new_iPhones = ["iPhone 12 Mini", "iPhone 12", "iPhone 12 Pro", "iPhone 12 Pro Max",
               "iPhone 13 Mini", "iPhone 13", "iPhone 13 Pro", "iPhone 13 Pro Max"]
