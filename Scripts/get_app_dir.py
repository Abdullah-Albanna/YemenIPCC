from . import (
    sys, os,
    cache
)

@cache
def getAppDirectory() -> str:
    """
    Gets the script or the
    executable path
    """
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    if bundle_dir.endswith("Scripts"):
        bundle_dir = bundle_dir[:-len("Scripts")]
    
    return bundle_dir