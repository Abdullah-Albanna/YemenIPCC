from . import (
    subprocess, tk, os,  messagebox, aiohttp, asyncio, textwrap, 
    Progressbar, Style, TemporaryDirectory, Event,
    List, new_iPhone_message, new_iPhones,
    sleep
                            )
from .variables_manager import VariableManager
from .thread_starter import startThread
from .check_for_internet import checkInternetConnection
from .logger_config_class import YemenIPCCLogger
from .send_data import sendData
from .get_bin_path import BinaryPaths
from .managed_process import managedProcess
from .resize_dpi import DPIResize
from .updating_status import DeviceManager
from .thread_terminator_var import terminate


logger = YemenIPCCLogger().logger
bin_paths = BinaryPaths().getPaths()

ideviceinfo = bin_paths["ideviceinfo"]
ideviceinstaller = bin_paths["ideviceinstaller"]
idevicediagnostics = bin_paths["idevicediagnostics"]
idevicesyslog = bin_paths["idevicesyslog"]
args = bin_paths["args"]

    
def readSysLog(log_queue, stop_event) -> None:
    """
    Reads the iPhone system logs to decide the result of the injection process
    """
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
        logger.debug("Stoppted readSysLog")

async def isFileDownloadable(url) -> bool:
    """
    Checks if the file exists or not by testing the downloading ability
    """
    try:
        # We well use aiohttp with async to get the fastest result
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
                if content_type in ['application/octet-stream', 'application/zip']:
                    return True

                return False
    except aiohttp.ClientError as e:
        logger.error(f"Error: {e}")
        return False

def removingAndInjectingIPCC(window: tk.Tk, log_text: tk.Text, selected_bundle: str, selected_container: str, app_font) -> None:
    
    """
    This is the main injection process.

    Args:
        window (tk.Tk): The tkinter window.
        log_text (tk.Text): The text widget for logger.
        selected_bundle (str): The selected bundle name.
        selected_container (str): The selected option name.
    """

    # Sets the running variable to True so the button stop working, to avoid multi-clicking the button
    VariableManager().setRunning(True)
    try:
        if not checkInternetConnection():
            messagebox.showerror("No Internet", "Please make sure to connect to the internet first")
            VariableManager().setRunning(False)
            logger.debug("User tried to inject without internet")
            return
        # Get product information
        product_version, product_type = DeviceManager().extractValuesFromLog()

        is_new_iPhone = False

        # Goes through the connected device, if it is a new phone, would display the usage
        for new_iPhone in new_iPhones:
            if not product_type == new_iPhone:
                continue
            logger.info("User have a new iPhone")
            messagebox.showinfo("Instructions", new_iPhone_message)
            is_new_iPhone = True

        # Create custom style for the progress bar. It looks better
        style = Style()
        style.theme_use('clam')

        # Configure colors and appearance for the custom style
        style.configure("Custom.Horizontal.TProgressbar",
                        background="#3b56bc", 
                        troughcolor="#FFFFFF",
                        bordercolor="#3b56bc",
                        lightcolor="#3b56bc", 
                        darkcolor="#3b56bc",  
                        troughrelief="flat",  
                        troughborderwidth=9,  
                        borderwidth=0,  # No border
                        relief="flat",  # Flat relief
                        )

        # Create progress frame
        progress_frame = tk.Frame(window, bg="#0a1750")  # Dark blue background
        progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Progress label
        progress_label = tk.Label(progress_frame, text="Checking the existence of the file...",
                                font=("Arial", 14), bg="#0a1750", fg="white")  # Adjust font and colors
        progress_label.pack(pady=5)

        # Progress bar
        progress_bar = Progressbar(progress_frame, orient="horizontal", length=300, mode="indeterminate",
                                style="Custom.Horizontal.TProgressbar")  # Use custom style
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

        selected_container: str = which_one_mappings.get(selected_container, "Your not suppose to see this message ): ")

        # URL for downloading IPCC
        url = f"https://raw.githubusercontent.com/Abdullah-Albanna/YemenIPCC/master/{replace_space(product_type)}/iOS%20{product_version}/Using%20{selected_container}/{replace_space(product_type)}_iOS_{product_version}_{selected_bundle}.ipcc"
        window.update_idletasks()
        downloadable = asyncio.run(isFileDownloadable(url))
        if not downloadable:
            # If the ipcc is note downloadable, stops the progress bar and pops an error
            logger.error("User have requested a bundle that is not avaliable")
            progress_bar.stop()
            progress_bar.destroy()
            progress_label.destroy()
            message = textwrap.dedent(f"""\
            Your requested bundle:

            iPhone model: {product_type}
            iPhone version: {product_version}
            Bundle: {selected_bundle}
            Container: {replace_perc20(selected_container)}

            is not available!

            It either hasn't been downloaded from the server or you selected an unsupported bundle.

            This error has been sent to the developer for further investigation.
            """)
            messagebox.showerror("Bundle not Found", message)
            return
        

        remove_bundle_file: str = os.path.join("."  ,"Removes", "Remove(default).ipcc")
        
        logger.info(f"URL: {url}")

        progress_label.config(text=f"Removing Old IPCC ...")
        window.update_idletasks()  # Update the label text

        # Remove old IPCC file
        with managedProcess([ideviceinstaller, "install", remove_bundle_file], **args) as remove_process:
            stdout = remove_process.communicate()[0]
            stderr = remove_process.communicate()[1]
            result = stdout + stderr

        # If validate is set, and it is not a new phone, it slows down a bit
        if VariableManager().getValidate() == True and not is_new_iPhone:
            sleep(20)  # Why?, well some devices need sometime to process the removal, so it waits for that
        else:
            # Else fast, because it is not needed to check
            sleep(7)

        if not "Could not connect to lockdownd. Exiting." in result:

            # Colors the logs
            if "SUCCESS: " in result:
                color = "green"
            elif "Install: Complete" in result:
                color = "green"
            elif "ERROR: " in result:
                logger.error(f"An error happened in the removal, error: {result}")
                color = "red"
            elif "No device found":
                color = "red"
            else:
                color = "grey"

            log_text.tag_configure(color, foreground=color)
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, f"\n{result}\n", color)
            log_text.see(tk.END)
        else:
            logger.error("Trust error")
            messagebox.showerror("Trust Error", "Please reconnect the usb and try again")
            progress_frame.destroy()

        # Sets up a temporary path for the selected .ipcc file to be downloaded to
        with TemporaryDirectory() as temp_dir:
            logger.debug(f"Temporary directory for the .ipcc: {temp_dir}")
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

                if VariableManager().getValidate() == True and not is_new_iPhone:
                    # If validate is set and is not a new iPhone, it would start the system logger right before injecting
                    log_queue = []
                    stop_event = Event()
                    startThread(target=lambda: readSysLog(log_queue, stop_event), name="read syslog", daemon=False)

                # Inject .ipcc
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
                        logger.error(f"An error accoured in the injection of the file, error: {result}")
                        color = "red"
                    elif "No device found":
                        color = "red"
                    else:
                        color = "grey"

                    log_text.tag_configure(color, foreground=color)
                    log_text.insert(tk.END, "------⸻⸻Injecting⸻⸻------")
                    log_text.insert(tk.END, f"\n{result}\n", color)
                    log_text.see(tk.END)

                if VariableManager().getValidate() == True and not is_new_iPhone:
                    progress_bar.stop()
                    progress_bar.destroy()
                    progress_label.destroy()

                    # Create new progress bar for validation
                    validate_progress_frame = tk.Frame(window, bg="#0a1750")
                    validate_progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                    validate_progress_label = tk.Label(validate_progress_frame, text="Validating...", font=(app_font, DPIResize(14)), bg="#0a1750", fg="white")
                    validate_progress_label.pack(pady=5)
                    validate_progress_bar = Progressbar(validate_progress_frame, orient="horizontal", length=300, mode="determinate", style="Custom.Horizontal.TProgressbar")
                    validate_progress_bar.pack(pady=5)

                    validate_progress_bar["maximum"] = 40
                    for second in range(40):
                        validate_progress_bar["value"] = second + 1
                        window.update_idletasks()
                        sleep(1)

                    # Collect logs from the syslog thread and stop it
                    logs_result = "\n".join(log_queue)
                    stop_event.set()
                else:
                    # Stops and destroy the progress frame
                    progress_bar.stop()
                    progress_frame.destroy()

            
            else:
                # If the download process failed
                logger.error("Could not download the file")
                window.update_idletasks()

            # This deletes the temp directory once done with it, over time, it can get a lot of temporary folders
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(temp_dir)

        # Validate the injection by checking the logs
        if VariableManager().getValidate() == True and not is_new_iPhone:
            # Only if it is not empty
            if logs_result != None or logs_result == "":
                # If the line "SIM is ready" in the logs, that means it is working
                if "SIM is ready" in logs_result:
                    logger.success("SIM is ready, injection was successful.")

                    log_text.tag_configure("green", foreground="green")
                    log_text.insert(tk.END, "----⸻⸻Validatation⸻⸻----")
                    log_text.insert(tk.END, f"\nInjection successful. SIM is ready.\n", "green")
                    log_text.see(tk.END)
                    asyncio.run(sendData("injection", device=product_type, success=True))
                else:
                    logger.error("SIM is not ready, injection failed.")

                    log_text.tag_configure("red", foreground="red")
                    log_text.insert(tk.END, "----⸻⸻Validatation⸻⸻----")
                    log_text.insert(tk.END, f"\nInjection failed. SIM is not ready.\n", "red")
                    log_text.see(tk.END)
                    asyncio.run(sendData("injection", device=product_type, success=False))
            else:
                logger.info("Could not validate the injection process")
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
                logger.info("User declined the restart of his new iPhone")
                continue

            with managedProcess([idevicediagnostics, "restart"], **args) as restart_process:
                stdout = restart_process.communicate()[0]
                stderr = restart_process.communicate()[1]
                if stdout:
                    logger.debug(stdout)
                elif stderr:
                    logger.warning(stderr)
            
    finally:
        # And finaly activates the button
        VariableManager().setRunning(False)

def injection(window: tk.Tk, log_text: tk.Text, selected_bundle: str, selected_container: str, app_font) -> None:

    """
    Remove old IPCC files and inject the selected one into the device.

    Args:
        window (tk.Tk): The tkinter window.
        log_text (tk.Text): The text widget for logger.
        selected_bundle (str): The selected bundle name.
        selected_container (str): The selected option name.
    """

    # The thread has to be run from here, or the progress bar won't work well
    startThread(lambda: removingAndInjectingIPCC(window, log_text, selected_bundle, selected_container, app_font), "removingAndInjectingIPCC")


def cleanRemove(window: tk.Tk, log_text: tk.Text, app_font) -> None:

    """
    Does a clean Network Configuration (aka IPCC) removal.
    It might be handy if the iPhone is cluttered with ipccs.

    Args:
        window: tk.Tk --> the tkinter window.
        log_text: tk.Text --> The text widget for logger
    """
    if not messagebox.askokcancel("Clean Bundles", 'Press "OK" if you want to start removing old bundles on the iPhone'):
        return

    VariableManager().setRunning(True)

    # Check if device is connected
    with managedProcess([ideviceinfo, '-s'], **args) as proc:
        stdout = proc.communicate()[0]
        stderr = proc.communicate()[1]
        result = stdout + stderr
        if "No device found" in result:
            logger.warning("There is was no device connected while doing a clean removal")
            log_text.tag_configure("yellow", foreground="yellow")
            log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            log_text.insert(tk.END, "\nNo device found, is it plugged in?\n", "yellow")
            log_text.see(tk.END)
            return
        
    # Create custom style for the progress bar. It looks better
    style = Style()
    style.theme_use('clam')

    # Configure colors and appearance for the custom style
    style.configure("Custom.Horizontal.TProgressbar",
                    background="#3b56bc",  
                    troughcolor="#FFFFFF",  
                    bordercolor="#3b56bc",  
                    lightcolor="#3b56bc",  
                    darkcolor="#3b56bc",  
                    troughrelief="flat",  
                    troughborderwidth=9,  # No trough border
                    borderwidth=0,  # No border
                    relief="flat",  # Flat relief
                    )

    # Create progress frame
    progress_frame = tk.Frame(window, bg="#0a1750")
    progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Progress label
    progress_label = tk.Label(progress_frame, text="Progress:", font=(app_font, DPIResize(14)), bg="#0a1750", fg="white")
    progress_label.pack(pady=5)

    # Progress bar
    progress_bar = Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", style="Custom.Horizontal.TProgressbar")
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
                logger.error(f"There was an error in the clean removal process, error: {result}")
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

    VariableManager().setRunning(False)


def disableIfRunning(button: tk.Button, window: tk.Tk) -> None:
    
    """
    Disables the button if the user is injecting an ipcc to avoid multi injecting


    Args:
        button: tk.Button
        window: tk.Tk
    
    """
    while not terminate.is_set():
        plugged = DeviceManager().checkIfPlugged()
        
        if VariableManager().getRunning():
            button.config(state=tk.DISABLED)
        else:
            button.config(state=tk.NORMAL if plugged else tk.DISABLED)
        sleep(0.5)
        window.update_idletasks()