from .projectimports import (subprocess, tk, messagebox, system, os, sleep, managedProcess, Union)
from .thread_starter import startThread
from .logging_config import setupLogging
import logging


setupLogging(debug=True, file_logging=True)

# What these three do is specifing the executeable binary for each system so the user do not have to install anything
if system == "Mac":

    # This sets the library looking path to the project's library, same thing we did in the injection.py
    os.environ['DYLD_LIBRARY_PATH'] = "./Scripts/mac_binary/lib:$DYLD_LIBRARY_PATH"

    # Copies the path so it could be passed to the subprocesses
    env = os.environ.copy()

    idevicepair: str = "./Scripts/mac_binary/idevicepair"

if system == "Linux":
    
    os.environ['LD_LIBRARY_PATH'] = "./Scripts/linux_binary/lib:$LD_LIBRARY_PATH"
    env = os.environ.copy()

    idevicepair: str = "./Scripts/linux_binary/idevicepair"

elif system == "Windows":

    idevicepair: str = ".\\Scripts\\windows_binary\\idevicepair.exe"
    env = os.environ.copy()
    args = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'text': True,
        'env': env,
        'creationflags': subprocess.CREATE_NO_WINDOW
    }

if system != "Windows":

    args = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True,
            'env': env
        }


def validateDevice() -> Union[str, bool]:

    """
    Validate the device connection.

    Returns:
        Union[str, bool]: A string indicating the validation status ("passcode", "accept", "success") or a boolean (True or False).
    """
    try:
    
        with managedProcess([idevicepair, "validate"], **args) as validate:
            stdout = validate.communicate()[0]
            stderr = validate.communicate()[1]
            result = stdout + stderr
        if "Please enter the passcode on the device and retry" in result:
            return "passcode"
        elif "Please accept the trust dialog on the screen of device" in result:
            return "accept"
        elif "Validated pairing with device" in result:
            return True
        elif "Device validation failed: unhandled error code -5" in result:
            return False
        elif "Please enter the passcode on the device and retry" in result:
            return False
        elif "said that the user denied the trust dialog." in result:
            return "denied"

    except subprocess.CalledProcessError as e:
        # If an error occurs during the subprocess, print the error message
        error_message: str = e.stderr.strip()
        print(error_message)

def repairiPhone(log_text) -> None:

    """
    Re-pair the iPhone connection.

    Args:
        log_text: The text widget to display log messages.
    """
    # Ask for confirmation before proceeding with iPhone re-pair
    if not messagebox.askyesno("Confirm", f"Are you sure that you want to re-pair connected iPhone from your {system}?"):
        return
    
    # Unpair the iPhone
    with managedProcess([idevicepair, "unpair"], **args) as unpair_process:
        stdout = unpair_process.communicate()[0]
        stderr = unpair_process.communicate()[1]
        result = stdout + stderr

    # To avoid it logging "No Device found." twice
    if "No device found, is it plugged in?" in result or "No device found." in result:
        startThread(lambda: pairAndCheck(log_text), "pairAndCheck", logging)
        return

    if "SUCCESS: " in result:
        color = "green"
    elif "ERROR: " in result:
        logging.error(f"repair.py - An error occurred in the repairiPhone(), error result: {result}")
        color = "red"
    elif "No device found.":
        color = "red"
    else:
        color = "grey"

    # Insert unpair log output into the log text widget if the device is plugged
    log_text.tag_configure(color, foreground=color)
    log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
    log_text.insert(tk.END, f"\n{result}\n", color)
    log_text.see(tk.END)

    # Start a thread to pair the iPhone again and check the validation
    startThread(lambda: pairAndCheck(log_text), "pairAndCheck", logging)

def pairAndCheck(log_text) -> None:
    
    """
    Pair the iPhone and check validation.

    Args:
        log_text: The text widget to display log messages.
    """
    # Keep trying to pair the iPhone and check validation
    while True:
        # Pair the iPhone
        with managedProcess([idevicepair, "pair"], **args) as pair:
            stdout = pair.communicate()[0]
            stderr = pair.communicate()[1]
            result = stdout + stderr

        if "SUCCESS: " in result:
            color = "green"
        elif "ERROR: " in result:
            logging.error(f"repair.py - An error occurred in the pairAndCheck(), error result: {result}")
            color = "red"
        elif "No device found.":
            color = "red"
        else:
            color = "grey"

        # Insert pair log output into the log text widget
        log_text.tag_configure(color, foreground=color)
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(tk.END, f"\n{result}\n", color)
        log_text.see(tk.END)

        # If pairing is successful, break the loop
        if "SUCCESS: Paired with device" in result:
            break

        # If device is not plugged, or the binary has bugs, it breaks out of the loop
        if "No device found, is it plugged in?" in result:
            break
        elif "No device found." in result:
            break
        elif "symbol lookup error" in result:
            logging.critical(f"repair.py - An error occurred, possibly library error, error: {result}")
            break
        elif "lockdownd_pair_cu" in result:
            logging.critical(f"repair.py - An error occurred, possibly library error, error: {result}")
            break


        # Validate the device and take action accordingly
        validation = validateDevice()
        if validation == "passcode":
            messagebox.showinfo("Trust", f"type your password in your phone to trust your {system} machine")
        elif validation == "accept":
            messagebox.showinfo("Accept", f"accept the trust dialog on the screen to trust your {system} machine")
        elif validation == "denied":
            messagebox.showerror("Error", "You denied the request, please reconnect the usb and try again!")
            break
        sleep(1)