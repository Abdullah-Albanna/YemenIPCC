from .projectimports import (subprocess, 
                            tk, 
                            Progressbar, 
                            TemporaryDirectory, 
                            os, sleep, Thread, List,
                            DeviceManager, VariableManager, messagebox, system,
                            new_iPhone_message, new_iPhones, DPIResize)

from .check_for_update import checkInternetConnection

# Load existing variables from the text file
saved_variables = VariableManager().loadSavedVariables()

# Set initial running state
running: bool = saved_variables.get('running', False)

# What these three do is specifing the executeable binary for each system so the user do not have to install anything
if system == "Mac":
  
    # This sets the library looking path to the project's library, again, to make the user not install anything
    os.environ['DYLD_LIBRARY_PATH'] = "./Scripts/mac_binary/lib:$DYLD_LIBRARY_PATH"

    # Copies the path so it could be passed to the subprocesses
    env = os.environ.copy()

    ideviceinfo: str = "./Scripts/mac_binary/ideviceinfo" 
    ideviceinstaller: str = "./Scripts/mac_binary/ideviceinstaller"
    idevicediagnostics: str = "./Scripts/mac_binary/idevicediagnostics"
    
if system == "Linux":

    # The same, but only change the env variable for linux
    os.environ['LD_LIBRARY_PATH'] = './Scripts/linux_binary/lib:$LD_LIBRARY_PATH'
    env = os.environ.copy()

    ideviceinfo: str = "./Scripts/linux_binary/ideviceinfo"
    ideviceinstaller: str = "./Scripts/linux_binary/ideviceinstaller"
    idevicediagnostics: str = "./Scripts/linux_binary/idevicediagnostics"

elif system == "Windows":
    
    ideviceinfo: str = ".\\Scripts\\windows_binary\\ideviceinfo.exe"
    ideviceinstaller: str = ".\\Scripts\\windows_binary\\ideviceinstaller.exe"
    idevicediagnostics: str = ".\\Scripts\\windows_binary\\idevicediagnostics.exe"
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
    saved_variables['running'] = running
    VariableManager().saveVariables(saved_variables)

# Get the current running state
def getRunning() -> bool:
    global running
    saved_variables = VariableManager().loadSavedVariables()
    running = saved_variables.get('running', "False")
    if running == "False":
        return False
    elif running == "True":
        return True


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
            return
        # Get product information
        product_version, product_type = DeviceManager().extractValuesFromLog()

        # Goes through the connected device, if it is a new phone, would display the usage
        for new_iPhone in new_iPhones:
            if not product_type == new_iPhone:
                continue
            messagebox.showinfo("Instructions", new_iPhone_message)

        # Create progress frame
        progress_frame: tk.Frame = tk.Frame(window, bg="#0a1750")
        progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Progress label
        progress_label: tk.Label = tk.Label(progress_frame, text="Progress:", font=(app_font, DPIResize(14)), bg="#0a1750", fg="white")
        progress_label.pack(pady=5)

        # Progress bar
        progress_bar: Progressbar = Progressbar(progress_frame, orient="horizontal", length=300, mode="indeterminate")
        progress_bar.pack(pady=5)


        remove_bundles_files: List[str] = [
            os.path.join("."  ,"Removes", "Remove(default).ipcc"),
        ]


        total_files = len(remove_bundles_files)

        for i, file_path in enumerate(remove_bundles_files, start=1):
            progress_label.config(text=f"Removing Old IPCC: {i}/{total_files}")
            window.update_idletasks()  # Update the label text

            # Remove old IPCC file
            remove_process: subprocess.Popen = subprocess.Popen([ideviceinstaller, "install", file_path], **args)
            stdout = remove_process.communicate()[0]
            stderr = remove_process.communicate()[1]
            result = stdout + stderr
            if not "Could not connect to lockdownd. Exiting." in result:

                # Colors the logs
                if "SUCCESS: " in result:
                    color = "green"
                elif "Install: Complete" in result:
                    color = "green"
                elif "ERROR: " in result:
                    color = "red"
                elif "No device found":
                    color = "red"
                else:
                    color = "grey"
                log_text.tag_configure(color, foreground=color)
                log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
                log_text.insert(tk.END, f"\n{result}\n", color)

                progress_bar["value"] = (i / total_files) * 100
                window.update_idletasks()
            else:
                messagebox.showerror("Trust Error", "Please reconnect the usb and try again")
                progress_frame.destroy()

        # A small reuseable function to replace any whitespace with nothing, used for the url
        replace_space: str = lambda s: s.replace(" ", "")

        # Converts the .ipcc type option for the url
        which_one_mappings: dict[str, str] = {
            'Default.bundle': "Default%20Bundle",
            'Unknown.bundle': "Unknown%20Bundle",
        }

        selected_which_one: str = which_one_mappings.get(selected_which_one, "Your not suppose to see this message ):, unless you're reading the code ;) ")

        # URL for downloading IPCC
        url = f"https://raw.githubusercontent.com/Abdullah-Albanna/YemenIPCC/master/{replace_space(product_type)}/iOS%20{product_version}/Using%20{selected_which_one}/{replace_space(product_type)}_iOS_{product_version}_{selected_bundle}.ipcc"

        # Sets up a temporary path for the .selected .ipcc file to be downloaded to
        with TemporaryDirectory() as temp_dir:
            progress_label.config(text=f"Downloading {selected_bundle} for {product_type}...")   
            window.update_idletasks()

            progress_bar.start(interval=50)  # Start the indeterminate progress bar
            
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
                sleep(7)  # Why?, well some devices need sometime to process the removal, so it waits for that
                injecting_process = subprocess.Popen([ideviceinstaller, "install", downloaded_file_path], **args)
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
                        color = "red"
                    elif "No device found":
                        color = "red"
                    else:
                        color = "grey"

                    log_text.tag_configure(color, foreground=color)
                    log_text.insert(tk.END, "------⸻⸻Injecting⸻⸻------")
                    log_text.insert(tk.END, f"\n{result}\n", color)
            
            else:
                # If the download process failed
                progress_label.config(text="Download failed")
                window.update_idletasks()

            # This deletes the temp directory once done with it, over time, it could get a lot temporary folders
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(temp_dir)

        # Stops and destroy the progress frame
        progress_bar.stop()
        progress_frame.destroy()

        # This is a just-in-case, if you have a new phone, it would ask if you want to restart the device
        for new_iPhone in new_iPhones:
            if not product_type == new_iPhone:
                continue
            if download_process.wait() != 0:
                continue
            if not messagebox.askyesno("Restart", f"Looks like you have {product_type}, you might need to restart it\n\n Do you want to restart your iPhone?"):
                continue

            subprocess.Popen([idevicediagnostics, "restart"], **args)
            
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
    Thread(target=lambda: removingAndInjectingIPCC(window, log_text, selected_bundle, selected_which_one, app_font), daemon=True).start()

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
    with subprocess.Popen([ideviceinfo, '-s'], **args) as proc:
        stdout = proc.communicate()[0]
        stderr = proc.communicate()[1]
        result = stdout + stderr
        if "No device found" in result:
            log_text.tag_configure("red", foreground="red")
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, "\nNo device found, is it plugged in?\n", "red")
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

        with subprocess.Popen([ideviceinstaller, "install", file_path], **args) as remove_proc:
            stdout = remove_proc.communicate()[0]
            stderr = remove_proc.communicate()[1]
            result = stdout + stderr

            if "SUCCESS: " in result:
                color = "green"
            elif "Install: Complete" in result:
                color = "green"
            elif "ERROR: " in result:
                color = "red"
            elif "No device found":
                color = "red"
            else:
                color = "grey"

            log_text.tag_configure(color, foreground=color)
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, f"\n{result}\n", color)

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