from .projectimports import (subprocess, tk, os, List, messagebox, system, new_iPhone_message, new_iPhones, aiohttp, asyncio, textwrap,
                            DPIResize, sleep, managedProcess,
                            Progressbar, DeviceManager, TemporaryDirectory, Thread, Event)
from .variables_manager import VariableManager
from .thread_starter import startThread
from .check_for_update import checkInternetConnection
from .logging_config import setupLogging
import logging


setupLogging(debug=True, file_logging=True)

# Load existing variables from the text file
try:
    temp_variables = VariableManager().loadTempVariables()
except Exception as e:
    logging.error(f"injection.py - Could not load the saved variables, error:{e}")

# Set initial running state
try:
    running: bool = temp_variables.get('running', False)
except Exception as e:
    logging.error("injection.py - Could not get the running status from the chache file")

# What these three do is specifing the executeable binary for each system so the user do not have to install anything
if system == "Mac":
  
    # This sets the library looking path to the project's library, again, to make the user not install anything
    os.environ['DYLD_LIBRARY_PATH'] = "./Scripts/mac_binary/lib:$DYLD_LIBRARY_PATH"

    # Copies the path so it could be passed to the subprocesses
    env = os.environ.copy()

    ideviceinfo: str = "./Scripts/mac_binary/ideviceinfo" 
    ideviceinstaller: str = "./Scripts/mac_binary/ideviceinstaller"
    idevicediagnostics: str = "./Scripts/mac_binary/idevicediagnostics"
    idevicesyslog: str = "./Scripts/mac_binary/idevicesyslog"
    
if system == "Linux":

    # The same, but only change the env variable for linux
    os.environ['LD_LIBRARY_PATH'] = './Scripts/linux_binary/lib:$LD_LIBRARY_PATH'
    env = os.environ.copy()

    ideviceinfo: str = "./Scripts/linux_binary/ideviceinfo"
    ideviceinstaller: str = "./Scripts/linux_binary/ideviceinstaller"
    idevicediagnostics: str = "./Scripts/linux_binary/idevicediagnostics"
    idevicesyslog: str = "./Scripts/linux_binary/idevicesyslog"

elif system == "Windows":
    
    ideviceinfo: str = ".\\Scripts\\windows_binary\\ideviceinfo.exe"
    ideviceinstaller: str = ".\\Scripts\\windows_binary\\ideviceinstaller.exe"
    idevicediagnostics: str = ".\\Scripts\\windows_binary\\idevicediagnostics.exe"
    idevicesyslog: str = ".\\Scripts\\windows_binary\\idevicesyslog.exe"
    env = os.environ.copy()

    # Adds the CREATE_NO_WINDOW for windows (hides the terminal)
    args = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'text': True,
        'env': env,
        'creationflags': subprocess.CREATE_NO_WINDOW
    }

# Don't for others, not needed for them and not even avaliable
if system != "Windows":

    args = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True,
            'env': env
        }
    
# Update the running state and save to the file
def setRunning(value: bool) -> None:

    global running
    running = value
    # Load existing variables from the text file
    try:
        saved_variables = VariableManager().loadTempVariables()
    except Exception as e:
        logging.error(f"injection.py - Could not load the saved variables, error:{e}")
    saved_variables['running'] = running
    VariableManager().saveVariables(saved_variables)

# Get the current running state
def getRunning() -> bool:

    global running
    # Load existing variables from the text file
    try:
        saved_variables = VariableManager().loadTempVariables()
    except Exception as e:
        logging.error(f"injection.py - Could not load the saved variables, error:{e}")
    running = saved_variables.get('running', "False")
    if running == "False":
        return False
    elif running == "True":
        return True
    
def getValidate() -> bool:
    # Load existing variables from the text file
    try:
        saved_variables = VariableManager().loadTempVariables()
    except Exception as e:
        logging.error(f"injection.py - Could not load the saved variables, error:{e}")

    validate = saved_variables.get('validate', "True")
    if validate == "False":
        return False
    elif validate == "True":
        return True

    
def read_syslog(log_queue, stop_event):
    syslog_process = subprocess.Popen([idevicesyslog], **args, universal_newlines=True)
    try:
        while not stop_event.is_set():
            output = syslog_process.stdout.readline().strip()
            if output == "" and syslog_process.poll() is not None:
                break
            if output:
                log_queue.append(output)
    finally:
        syslog_process.terminate()
        syslog_process.wait()

async def isFileDownloadable(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True) as response:
                # Check if the request was successful
                if response.status != 200:
                    return False

                # Get the content type
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Check if the content type is not HTML
                if 'text/html' in content_type:
                    return False

                # Check for Content-Disposition header to see if it's an attachment
                content_disposition = response.headers.get('Content-Disposition', '').lower()
                if 'attachment' in content_disposition:
                    return True
                
                # If there is no Content-Disposition header, infer from content type
                if content_type in ['application/octet-stream', 'application/pdf', 'application/zip']:
                    return True

                return False
    except aiohttp.ClientError as e:
        print(f"Error: {e}")
        return False

def removingAndInjectingIPCC(window: tk.Tk, log_text: tk.Text, selected_bundle: str, selected_which_one: str, app_font) -> None:
    
    """
    This is where the main injecting happens

    Args:
        window: tk.Tk -> the tkinter window.
        log_text: tk.Text -. the tkinter Text widget.
        selected_bundle: str -> the current selected bundle
        selected_which_one: str -> the current selected ipcc type
    """

    # Sets the running variable to True so the button stop working, to avoid multi-clicking the button
    setRunning(True)
    try:
        if not checkInternetConnection():
            messagebox.showerror("No Internet", "Please make sure to connect to the internet first")
            setRunning(False)
            logging.debug("injection.py - User tried to inject without internet")
            return
        # Get product information
        product_version, product_type = DeviceManager().extractValuesFromLog()
        
        logging.info(f"injection.py - iPhone model: {product_type}, iPhone version: {product_version}")

        is_new_iPhone = False

        # Goes through the connected device, if it is a new phone, would display the usage
        for new_iPhone in new_iPhones:
            if not product_type == new_iPhone:
                continue
            logging.info("injection.py - User have a new iPhone")
            messagebox.showinfo("Instructions", new_iPhone_message)
            is_new_iPhone = True

        # Create progress frame
        progress_frame: tk.Frame = tk.Frame(window, bg="#0a1750")
        progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Progress label
        progress_label: tk.Label = tk.Label(progress_frame, text="Checking the existence of the file...", font=(app_font, DPIResize(14)), bg="#0a1750", fg="white")
        progress_label.pack(pady=5)

        # Progress bar
        progress_bar: Progressbar = Progressbar(progress_frame, orient="horizontal", length=300, mode="indeterminate")
        progress_bar.pack(pady=5)

        progress_bar.start(interval=50)  # Start the indeterminate progress bar

        # A small reuseable function to replace any whitespace with nothing and %20 with a dot, used for the url and a message
        replace_space: str = lambda s: s.replace(" ", "")
        replace_perc20: str = lambda s: s.replace("%20", " ").lower()

        # Converts the .ipcc type option for the url
        which_one_mappings: dict[str, str] = {
            'default.bundle': "Default%20Bundle",
            'unknown.bundle': "Unknown%20Bundle",
        }

        selected_which_one: str = which_one_mappings.get(selected_which_one, "Your not suppose to see this message ): ")

        # URL for downloading IPCC
        url = f"https://raw.githubusercontent.com/Abdullah-Albanna/YemenIPCC/master/{replace_space(product_type)}/iOS%20{product_version}/Using%20{selected_which_one}/{replace_space(product_type)}_iOS_{product_version}_{selected_bundle}.ipcc"
        downloadable = asyncio.run(isFileDownloadable(url))
        if not downloadable:
            logging.error("injection.py - User have requested a bundle that is not avaliable")
            progress_bar.stop()
            progress_bar.destroy()
            progress_label.destroy()
            message = textwrap.dedent(f"""\
            Your requested bundle:

            iPhone model: {product_type}
            iPhone version: {product_version}
            Bundle: {selected_bundle}
            Container: {replace_perc20(selected_which_one)}

            is not available!

            It either hasn't been downloaded from the server or you selected an unsupported bundle.

            This error has been sent to the developer for further investigation.
            """)
            messagebox.showerror("Bundle not Found", message)
            return
        
        remove_bundles_files: List[str] = [
            os.path.join("."  ,"Removes", "Remove(default).ipcc"),
        ]
        total_files = len(remove_bundles_files)
        
        logging.info(f"injection.py - Url is: {url}")

        for i, file_path in enumerate(remove_bundles_files, start=1):
            progress_label.config(text=f"Removing Old IPCC: {i}/{total_files}")
            window.update_idletasks()  # Update the label text

            # Remove old IPCC file
            with managedProcess([ideviceinstaller, "install", file_path], **args) as remove_process:
                stdout = remove_process.communicate()[0]
                stderr = remove_process.communicate()[1]
                result = stdout + stderr

            if getValidate() == True and not is_new_iPhone:
                sleep(20)  # Why?, well some devices need sometime to process the removal, so it waits for that
            else:
                sleep(7)

            if not "Could not connect to lockdownd. Exiting." in result:

                # Colors the logs
                if "SUCCESS: " in result:
                    color = "green"
                elif "Install: Complete" in result:
                    color = "green"
                elif "ERROR: " in result:
                    logging.warning(f"injection.py - An error happened in the removal, error: {result}")
                    color = "red"
                elif "No device found":
                    color = "red"
                else:
                    color = "grey"
                log_text.tag_configure(color, foreground=color)
                log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
                log_text.insert(tk.END, f"\n{result}\n", color)
                log_text.see(tk.END)

                progress_bar["value"] = (i / total_files) * 100
                window.update_idletasks()
            else:
                logging.error("injection.py - Trust error")
                messagebox.showerror("Trust Error", "Please reconnect the usb and try again")
                progress_frame.destroy()

        # Sets up a temporary path for the .selected .ipcc file to be downloaded to
        with TemporaryDirectory() as temp_dir:
            logging.debug(f"injection.py - Temporary directory for the .ipcc is: {temp_dir}")
            progress_label.config(text=f"Downloading {selected_bundle} for {product_type}...")   
            window.update_idletasks()
            
            # Gets the current directory and saves it for later
            last_dir = os.getcwd()

            # We go to the temporary directory so it would download there (can be used in other ways, but I find this the best for cross-platform)
            os.chdir(temp_dir)
            download_command = f'curl -L -OJL "{url}"'

            download_process = subprocess.Popen(download_command,shell=True, **args, universal_newlines=True)

            # Now we go back so we can continue with the rest
            os.chdir(last_dir)
            total_size = None
            while True:
                # Read stderr stream
                output = download_process.stderr.readline().strip()
                if output == '' and download_process.poll() is not None:
                    break

                # Parse progress information
                if not " % " in output:
                    continue
                parts = output.split()
                # Ensure that the line contains enough parts to parse progress information
                if not len(parts) >= 9:
                    continue
                # Check if the parts represent valid numbers before converting
                if not parts[1].isdigit() and not parts[6].isdigit():
                    continue
                total_size = int(parts[1])
                downloaded = int(parts[6])
                progress = int((downloaded / total_size) * 100)
                progress_bar["value"] = progress
                window.update_idletasks()

            # Wait for the download process to finish
            if download_process.wait() == 0:
                # Extract the downloaded file path
                downloaded_file_path = os.path.join(temp_dir, os.path.basename(url))

                # Update progress label
                progress_label.config(text=f"Injecting {selected_bundle}.IPCC to {product_type}")
                window.update_idletasks()

                # Inject .ipcc
                if getValidate() == True and not is_new_iPhone:
                    log_queue = []
                    stop_event = Event()
                    log_thread = Thread(target=read_syslog, args=(log_queue, stop_event))
                    log_thread.start()

                with managedProcess([ideviceinstaller, "install", downloaded_file_path], **args) as injecting_process:
                    stdout = injecting_process.communicate()[0]
                    stderr = injecting_process.communicate()[1]
                    result = stdout + stderr
                
                if not "Could not connect to lockdownd. Exiting." in result:
                    
                    # Red if error, Green if success
                    if "SUCCESS: " in result:
                        color = "green"
                    elif "Install: Complete" in result:
                        color = "green"
                    elif "ERROR: " in result:
                        logging.warning(f"injection.py - An error accoured in the injection of the file, error: {result}")
                        color = "red"
                    elif "No device found":
                        color = "red"
                    else:
                        color = "grey"

                    log_text.tag_configure(color, foreground=color)
                    log_text.insert(tk.END, "------⸻⸻Injecting⸻⸻------")
                    log_text.insert(tk.END, f"\n{result}\n", color)
                    log_text.see(tk.END)

                if getValidate() == True and not is_new_iPhone:
                    progress_bar.stop()
                    progress_bar.destroy()
                    progress_label.destroy()
                    # Create new progress bar for validation
                    validate_progress_frame = tk.Frame(window, bg="#0a1750")
                    validate_progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                    validate_progress_label = tk.Label(validate_progress_frame, text="Validating...", font=(app_font, DPIResize(14)), bg="#0a1750", fg="white")
                    validate_progress_label.pack(pady=5)
                    validate_progress_bar = Progressbar(validate_progress_frame, orient="horizontal", length=300, mode="determinate")
                    validate_progress_bar.pack(pady=5)

                    validate_progress_bar["maximum"] = 40
                    for second in range(40):
                        validate_progress_bar["value"] = second + 1
                        window.update_idletasks()
                        sleep(1)

                    # Collect logs from the syslog thread
                    logs_result = "\n".join(log_queue)
                    stop_event.set()
                else:
                    # Stops and destroy the progress frame
                    progress_bar.stop()
                    progress_frame.destroy()

            
            else:
                # If the download process failed
                logging.error("injection.py - Could not download the file")
                window.update_idletasks()

            # This deletes the temp directory once done with it, over time, it can get a lot temporary folders
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(temp_dir)

        # Validate the injection by checking the logs
        if getValidate() == True and not is_new_iPhone:
            if logs_result != None or logs_result == "":
                if "SIM is ready" in logs_result:
                    logging.info("injection.py - SIM is ready, injection was successful.")

                    log_text.tag_configure("green", foreground="green")
                    log_text.insert(tk.END, "----⸻⸻Validatation⸻⸻----")
                    log_text.insert(tk.END, f"\nInjection successful. SIM is ready.\n", "green")
                    log_text.see(tk.END)
                else:
                    logging.error("injection.py - SIM is not ready, injection failed.")

                    log_text.tag_configure("red", foreground="red")
                    log_text.insert(tk.END, "----⸻⸻Validatation⸻⸻----")
                    log_text.insert(tk.END, f"\nInjection failed. SIM is not ready.\n", "red")
                    log_text.see(tk.END)
            else:
                log_text.tag_configure("grey", foreground="grey")
                log_text.insert(tk.END, "----⸻⸻Validatation⸻⸻----")
                log_text.insert(tk.END, f"\nCould not validate\n", "grey")
                log_text.see(tk.END)
            
            validate_progress_bar.destroy()
            validate_progress_label.destroy()
        window.update_idletasks()

        # This is a just-in-case, if you have a new phone, it would ask if you want to restart the device
        for new_iPhone in new_iPhones:
            if product_type != new_iPhone:
                continue
            if download_process.wait() != 0:
                continue
            if not messagebox.askyesno("Restart", f"Looks like you have {product_type}, you might need to restart it\n\n Do you want to restart your iPhone?"):
                logging.info("injection.py - User declined the restart of his new iPhone")
                continue

            managedProcess([idevicediagnostics, "restart"], **args)
            
    finally:

        # And finaly activates the button
        setRunning(False)

def injection(window: tk.Tk, log_text: tk.Text, selected_bundle: str, selected_which_one: str, app_font) -> None:

    """
    Remove old IPCC files and inject the selected one into the device.

    Args:
        window (tk.Tk): The tkinter window.
        log_text (tk.Text): The text widget for logging.
        selected_bundle (str): The selected bundle name.
        selected_which_one (str): The selected option name.
    """

    # The thread has to be run from here, otherwise, the log autoscroll won't work for somereason
    startThread(lambda: removingAndInjectingIPCC(window, log_text, selected_bundle, selected_which_one, app_font), "removingAndInjectingIPCC", logging)


def cleanRemove(window: tk.Tk, log_text: tk.Text, app_font) -> None:

    """
    Does a clean Network Configuration (aka IPCC) removal.
    It might be handy if the iPhone is cluttered with ipccs.

    Args:
        window: tk.Tk --> the tkinter window.
        log_text: tk.Text --> The text widget for logging
    """
    if not messagebox.askokcancel("Clean Bundles", 'Press "OK" if you want to start removing old bundles on the iPhone'):
        return

    setRunning(True)

    # Check if device is connected
    with managedProcess([ideviceinfo, '-s'], **args) as proc:
        stdout = proc.communicate()[0]
        stderr = proc.communicate()[1]
        result = stdout + stderr
        if "No device found" in result:
            logging.warning("injection.py - There is no device connected while doing a clean removal")
            log_text.tag_configure("red", foreground="red")
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, "\nNo device found, is it plugged in?\n", "red")
            log_text.see(tk.END)
            return

    # Create progress frame
    progress_frame = tk.Frame(window, bg="#0a1750")
    progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Progress label
    progress_label = tk.Label(progress_frame, text="Progress:", font=(app_font, DPIResize(14)), bg="#0a1750", fg="white")
    progress_label.pack(pady=5)

    # Progress bar
    progress_bar = Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=5)

    # Files to remove
    remove_bundles_files: List[str] = [
        os.path.join("." , "Removes", f"Remove({name}).ipcc") for name in [
            "CellularSouth", "ChinaCN", "ChinaHK", "ChinaUSIM", "CWW", "default", "unknown", "USCellular"
        ]
    ]

    total_files = len(remove_bundles_files)

    # Remove bundles and update progress
    for i, file_path in enumerate(remove_bundles_files, start=1):
        progress_label.config(text=f"Removing Old IPCC: {i}/{total_files}")
        window.update_idletasks()  # Update the label text

        with managedProcess([ideviceinstaller, "install", file_path], **args) as remove_proc:
            stdout = remove_proc.communicate()[0]
            stderr = remove_proc.communicate()[1]
            result = stdout + stderr

            if "SUCCESS: " in result:
                color = "green"
            elif "Install: Complete" in result:
                color = "green"
            elif "ERROR: " in result:
                logging.error(f"injection.py - There was an error in the clean removal process, error: {result}")
                color = "red"
            elif "No device found":
                color = "red"
            else:
                color = "grey"

            log_text.tag_configure(color, foreground=color)
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, f"\n{result}\n", color)
            log_text.see(tk.END)

        progress_bar["value"] = (i / total_files) * 100
        window.update_idletasks()

    # Destroy progress frame
    progress_frame.destroy()

    setRunning(False)


def disableIfRunning(button: tk.Button, window: tk.Tk) -> None:
    
    """
    Disables the button if the user is injecting an ipcc to avoid multi injecting


    Args:
        button: tk.Button
        window: tk.Tk
    
    """
    while True:
        isrunning = getRunning()
        plugged = DeviceManager().checkIfPlugged()
        
        if isrunning:
            button.config(state=tk.DISABLED)
        else:
            button.config(state=tk.NORMAL if plugged else tk.DISABLED)
        sleep(0.5)
        window.update_idletasks()