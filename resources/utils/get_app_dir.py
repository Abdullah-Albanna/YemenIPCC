import sys
import os
from pathlib import Path


def getAppDirectory() -> Path:
    """
    Gets the script or the
    executable path
    """
    if getattr(sys, "frozen", False):
        # running in a bundle
        # bundle_dir = os.path.dirname(sys.executable)
        bundle_dir = Path(sys.executable).resolve().parent
        
    else:
        # running in a normal Python environment
        # bundle_dir = os.path.dirname(os.path.abspath(__file__))
        bundle_dir = Path(__file__).resolve().parent
        
    # keeps going back until the "resources" folder is in the listing of that dir
    while "resources" not in os.listdir(bundle_dir):
        bundle_dir = Path(bundle_dir).resolve().parent

    return bundle_dir


def getExecutablePath() -> Path:
    """
    Gets the actual executable binary path, whether it was frozen or not
    """
    bin_path = sys.argv[0]
    # full_bin_path = os.path.abspath(bin_path)
    full_bin_path = Path(bin_path).resolve().parent

    return full_bin_path
