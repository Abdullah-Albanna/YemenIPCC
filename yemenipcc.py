from Scripts.check_for_update import (checkForUpdate)
from Scripts.fixing_the_window import (initialize)
from Scripts.changing_option import (VariableManager)
from Scripts.injection import (injection, disableIfRunning)
from Scripts.updating_status import (updateButtonStateThreaded, updateLabelStateThreaded)
from Scripts.main_window import (logText, radioButtons, frames, windowCreation, menuBarCreation)
from Scripts.thread_starter import startThread
from Scripts.set_exec_perm import setExecutePermission

from Scripts.projectimports import (tk, Button, List, os, platform, family_font, gettempdir, font, messagebox, sleep, getAppDirectory, DPIResize, Path, managedProcess, glob)
from Scripts.logging_config import setupLogging
import logging
if platform.system() == "Darwin":
    from ttwidgets.ttwidgets import Button # type: ignore


# Sets up the logging
setupLogging(debug=True, file_logging=True)

# App current version
current_version: str = "1.1.0"

# Gets the current selected option from the the temp file
def getSelectedOption() -> None:
    # Globals it to used in threads
    global selected_bundle, selected_which_one

    # Variables for retrying
    attempts = 0 # Current attempt
    max_attempts = 3 # maximun attempt
    cache_loaded = False # Prevents logging from repeating 

    while True:
        if os.path.exists(os.path.join(tempdir, "yemenipcc_temp_variables.txt")):
            # Loads the variables if the file exists
            temp_variables = VariableManager().loadTempVariables()
            selected_bundle = temp_variables.get('selected_bundle', 'CellularSouthLTE')
            selected_which_one = temp_variables.get('selected_which_one', 'default.bundle')
            sleep(0.5)
            # If it has already been logged, do not log it again
            if not cache_loaded:
                logging.debug("Chache file exists, got the variables")
                cache_loaded = True
        else:
            logging.warning("Chache file dose not exists, creating one")
            # If it does not exists, it goes through steps
            try:
                try:
                    if not os.path.exists(tempdir):
                        # Creates the temporary folder if it does not exists, has been reported on newly installed macOS machines
                        logging.info("The temporary directory does not exists, making one")
                        Path(tempdir).mkdir(parents=True, exist_ok=True)
                    
                    # Then creats it in another way, why?, why not :)
                    Path(os.path.join(tempdir, "yemenipcc_temp_variables.txt")).touch()
                    attempts = 0  # Reset attempts if the file is successfully created
                    logging.info("Made the cache file with pathlib")

                except PermissionError as pe:
                    sleep(0.5)
                    logging.error(f"Not enough permissions to make the cache file, error: {pe}")
                    break

            except Exception as e:

                logging.debug(f"Attempt {attempts + 1} in creating the cache file failed, error: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    logging.error("Could not create 'yemenipcc_temp_variables.txt' after 3 attempts. Exiting loop.")
                    break

            sleep(0.5)

    # If nothing works, just use the default options, this would not happen, but just in case
    selected_bundle = "CellularSouthLTE"
    selected_which_one = "Default.bundle"
    logging.critical("Default options has been set, you cannot change options due to errors!")

    sleep(0.5)
    messagebox.showwarning("Cache Error", "There was a problem creating a cache file \n You can only use default bundles")


def main() -> None:

    # Used to change the radio button options
    x: tk.IntVar = tk.IntVar()
    y: tk.IntVar = tk.IntVar()

    # Creates the Tk window things with debuging 
    try:
        windowCreation(window)
        logging.debug("Made the window")
    except Exception as e:
        logging.error(f"An error occurred while creating the window, error: {e}")

    # Creates the menu bar option and commands with debuging
    try:
        menuBarCreation(window, current_version, app_font)
        logging.debug("Made the menu bar")
    except Exception as e:
        logging.error(f"An error occurred while creating the menu bar, error: {e}")

    # Creates the label to indicate the device is connected or not
    Stats: tk.Label = tk.Label(window, text="Disconnected", font=(app_font, DPIResize(30)), bg="#0a1750",  # Light Blue > < Dark Blue
                               fg="red",)
    Stats.pack(anchor=tk.NW, side="top", fill="both")

    # Main inject button creation
    button: tk.Button = Button(window,
                    text="Inject",
                    font=(app_font, DPIResize(27), "bold"),
                    relief=tk.RAISED,
                    command=lambda: injection(window, log_text, selected_bundle, selected_which_one, app_font),
                    bd=10,
                    padx=100,
                    fg="green",
                    bg="#030b2c", # Dark Blue
                    activebackground="#030b2c", # Dark Blue
                    activeforeground="#3b56bc", # Light Blue
                    state=tk.DISABLED
                    )
    

    # Sets the individual frames and set it to a variable to be used for other functions
    try:
        frame: tk.Frame = frames(window)
        logging.debug("Made the frames")
    except Exception as e:
        logging.error(f"An error occurred while creating the frames, error: {e}")

    # Same thing 
    try:
        radioButtons(which_one, bundles, x, y, app_font)
        logging.debug("Made the radio buttons")
    except Exception as e:
        logging.error(f"An error occurred while creating the radio buttons, error: {e}")

    # Same thing
    try:
        log_text: tk.Text = logText(app_font)
        logging.debug("Made the log text")
    except Exception as e:
        logging.error(f"An error occurred while creating the log text, error: {e}")

    # Necessary threads for the app to function with debuging
    startThread(lambda: disableIfRunning(button, window), "disableIfRunning", logging)
    startThread(lambda: checkForUpdate(current_version), "checkForUpdate", logging)
    startThread(lambda: updateButtonStateThreaded(window, frame, button, log_text, Stats), "updateButtonStateThreaded", logging)
    startThread(lambda: updateLabelStateThreaded(window, frame, button, log_text, Stats), "updateLabelStateThreaded", logging)
    startThread(getSelectedOption, "getSelectedOption", logging)


    # For some reason, I had to put it down here so it would be set down the window
    button.pack(side="bottom", fill="both")


    # Starts the window fixies (sets it to the center)
    try:
        initialize(window)
        logging.debug("Made the initialization of the window")
    except Exception as e:
        logging.error(f"An error occurred while initializing window, error: {e}")

    # And shows the window, YAY!
    window.mainloop()
    


if __name__ == "__main__":
    # Initial variables
    system = platform.system()
    window: tk.Tk = tk.Tk()
    window.focus()
    app_font = font.Font(family=family_font, size=DPIResize(14) if system == "Mac" or system == "Linux" else DPIResize(10))
    logging.debug("Made the app_font variable")

    tempdir = gettempdir() if system == "Windows" else os.path.join(os.path.expanduser("~/.cache"))
    bundles: List[str] = ["CellularSouthLTE", "USCellularLTE", "China", "ChinaUSIM", "ChinaHK", "CWW"]
    which_one: List[str] = ["default.bundle", "unknown.bundle"]
    logging.debug(f"OS: {platform.platform()}")

    # This is necessary, it changes to the app directory so the app would run normally if you run the script from another directory
    app_directory = getAppDirectory()
    logging.debug(f"App directory is: {app_directory}")
    logging.debug(f"Current directory: {os.getcwd()}")

    # Logs the distro
    if system == "Linux":
        logging.debug(f"Linux Distribution: {platform.freedesktop_os_release().get('PRETTY_NAME')}")
        logging.debug(f"Linux Version: {platform.freedesktop_os_release().get('VERSION')}")

    # If the current running directory is in the macOS bundle app,
    # or there is no folder called "Scripts" in the currrent directory then change the current directory to the executed script directory
    if app_directory.endswith("/Content/MacOS") or not os.path.exists(os.path.join(os.getcwd(), "Scripts")):
        os.chdir(app_directory)
        logging.debug(f"Switched directory to {app_directory}")

    # This will create the file if it doesn't exist or earse the content if it does
    try:
        with open(os.path.join(tempdir, "yemenipcc_temp_variables.txt"), 'w'):
            pass
        logging.debug("Made the chache file")

    except Exception as e:
        logging.error(f"Something wrong with making the chache file, error: {e}")


    # with open(os.path.join(".", "__version__"), 'w') as file:
        # file.write(current_version)


    # It just automates the process, to make it easier for noobs
    pattern = os.path.join(".", "Scripts", "*_binary")  # This just takes the binary folders
    matching_folders = glob.glob(pattern) # And this applies the wildcard
    for folder_path in matching_folders:
        if not "windows_binary" in folder_path : # not necessary for windows
            if "mac_binary" in folder_path and system != "Darwin": #  If it detects the mac biinary and it is not a mac machine, skip
                continue
            elif "linux_binary" in folder_path and system != "Linux": # Same
                continue
            # Sets the permission
            setExecutePermission(folder_path)

    main()