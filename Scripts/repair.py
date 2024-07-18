from . import (
    subprocess, tk, messagebox, 
    Union,
    sleep
    )
from .thread_starter import startThread
from .logger_config_class import YemenIPCCLogger 
from .get_bin_path import BinaryPaths
from .get_system import system
from .managed_process import managedProcess


logger = YemenIPCCLogger().logger
bin_paths = BinaryPaths().getPaths()

idevicepair = bin_paths["idevicepair"]
args = bin_paths["args"]


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
        error_message: str = e.stderr.strip()
        logger.error(error_message)

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

    # To avoid it logger "No Device found." twice
    if "No device found, is it plugged in?" in result or "No device found." in result:
        startThread(lambda: pairAndCheck(log_text), "pairAndCheck")
        return

    if "SUCCESS: " in result:
        color = "green"
        logger.debug("unPaired with the device successfully")
    elif "ERROR: " in result:
        if not "Please accept the trust dialog on the screen of device" in result:
            if not "is not paired with this host" in result:
                logger.warning(f"An error occurred in the repairiPhone(), error result: {result}")
        color = "red"
    elif "No device found.":
        color = "red"
    elif "Please accept the trust dialog on the screen of device" in result:
        color = "blue"
    else:
        color = "grey"

    # Insert unpair log output into the log text widget if the device is plugged
    log_text.tag_configure(color, foreground=color)
    log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
    log_text.insert(tk.END, f"\n{result}\n", color)
    log_text.see(tk.END)

    # Start a thread to pair the iPhone again and check the validation
    startThread(lambda: pairAndCheck(log_text), "pairAndCheck")

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
            logger.debug("Paired with the device successfully")
        elif "ERROR: " in result:
            if not "Please enter the passcode on the device" in result: 
                if not "Please accept the trust dialog on the screen of device"  in result:
                    color = "red"
                    logger.error(f"An error occurred in the pairAndCheck(), error result: {result}")
            color = "yellow"
        elif "No device found.":
            color = "yellow"
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
            logger.critical(f"An error occurred, possibly library error, error: {result}")
            break
        elif "lockdownd_pair_cu" in result:
            logger.critical(f"An error occurred, possibly library error, error: {result}")
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