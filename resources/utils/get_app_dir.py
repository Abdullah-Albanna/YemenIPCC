import sys
import os
from pathlib import Path


def getAppDirectory() -> str:
    """
    Gets the script or the
    executable path
    """
    if getattr(sys, "frozen", False):
        # running in a bundle
        bundle_dir = os.path.dirname(sys.executable)

    else:
        # running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    # keeps going back until the "resources" folder is in the listing of that dir
    while "resources" not in os.listdir(bundle_dir):
        bundle_dir = str(Path(bundle_dir).parent)

    return bundle_dir


def getExecutablePath():
    """
    Gets the actual executable binary path, whether it was frozen or not
    """
    bin_path = sys.argv[0]
    full_bin_path = os.path.abspath(bin_path)

    return str(Path(full_bin_path).parent)
