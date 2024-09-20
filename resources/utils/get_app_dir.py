import sys
import os
from pathlib import Path
from functools import cache


@cache
def getAppDirectory() -> str:
    """
    Gets the script or the
    executable path
    """
    if getattr(sys, "frozen", False):
        # Running in a bundle
        bundle_dir = os.path.dirname(sys.executable)
        
    else:
        # Running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
        
    if bundle_dir.endswith("utils"):
        bundle_dir = bundle_dir[: -len("resources/utils")]

    return bundle_dir

@cache
def getExecutablePath():
    return str(Path(os.path.abspath(sys.argv[0])).parent)