import platform
from typing import Literal, Union

bsystem = platform.system()
system: Union[Literal["Mac", "Windows", "Linux"], str] = ""

# Used to change the "Darwin" to "Mac" because it is known better with Mac not Darwin
if bsystem == "Darwin":
    system = "Mac"
else:
    system = bsystem
