import platform
from typing import Literal

bsystem = platform.system()
system: Literal["Mac", "Windows", "Linux"] = ""

# Used to change the "Darwin" to "Mac" because it is known better with Mac not Darwin
if bsystem == "Darwin":
    system = "Mac"
else:
    system = bsystem
