from Scripts import (
    tk, os, platform, font, messagebox, glob, asyncio, webbrowser, signal, 
    Button, Path, 
    List, 
    gettempdir, sleep
    )
from Scripts.check_for_update import (checkForUpdate)
from Scripts.fixing_the_window import (initialize)
from Scripts.changing_option import (VariableManager)
from Scripts.injection import (injection, disableIfRunning)
from Scripts.updating_status import (updateButtonStateThreaded, updateLabelStateThreaded)
from Scripts.main_window import (logText, radioButtons, frames, windowCreation, menuBarCreation)
from Scripts.thread_starter import startThread

from Scripts.set_exec_perm import setExecutePermission
from Scripts.logger_config_class import YemenIPCCLogger
from Scripts.win_console_allocation import winLogsInit
from Scripts.send_data import sendData
from Scripts.temp_uuid import createNewUUID, getUUID
from Scripts.check_version_validation import getVersionValidation
from Scripts.get_system import system
from Scripts.get_default_font import getDefaultFont
from Scripts.get_app_dir import getAppDirectory
from Scripts.resize_dpi import DPIResize
from Scripts.check_for_internet import checkInternetConnection
from Scripts.thread_terminator_var import terminate
from Scripts.exit_handle import handleExit
from Scripts.dict_control import DictControl

# App current version
current_version: str = "1.1.0"

def getSelectedOption() -> None:
    """
    Gets current selected bundle/container
    """
    global selected_bundle, selected_container

    # Variables for retrying
    attempts = 0 # Current attempt
    max_attempts = 3 # maximum attempt

    while True:
        if terminate.is_set():
            break
        if os.path.exists(os.path.join(tempdir, "yemenipcc","yemenipcc_temp_variables.txt")):
            # Loads the variables if the file exists
            temp_variables = VariableManager().loadTempVariables()
            selected_bundle = temp_variables.get('selected_bundle', 'CellularSouthLTE')
            selected_container = temp_variables.get('selected_container', 'default.bundle')
            sleep(0.5)
            # If it has already been logged, do not log it again
            if DictControl().shouldRun('Cache loaded'):
                logger.debug("Chache file exists, got the variables")
        else:
            logger.warning("Chache file dose not exists, creating one")
            # If it does not exists, it goes through steps
            try:
                try:
                    if not os.path.exists(tempdir):
                        # Creates the temporary folder if it does not exists, has been reported on newly installed macOS machines
                        logger.info("The temporary directory does not exists, making one")
                        Path(tempdir).mkdir(parents=True, exist_ok=True)
                    
                    # Then creats it in another way, why?, why not :)
                    Path(os.path.join(tempdir, "yemenipcc")).mkdir()
                    Path(os.path.join(tempdir, "yemenipcc", "yemenipcc_temp_variables.txt")).touch()
                    attempts = 0  # Reset attempts if the file is successfully created
                    logger.info("Made the cache file with pathlib")

                except PermissionError as pe:
                    sleep(0.5)
                    logger.error(f"Not enough permissions to make the cache file, error: {pe}")
                    break

            except Exception as e:

                logger.debug(f"Attempt {attempts + 1} in creating the cache file failed, error: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    logger.error("Could not create 'yemenipcc_temp_variables.txt' after 3 attempts. Exiting loop.")
                    break
            
            sleep(0.5)

    # If nothing works, just use the default options, this would not happen, but just in case
    selected_bundle = "CellularSouthLTE"
    selected_container = "default.bundle"
    logger.critical("Default options has been set, you cannot change options due to errors!")

    sleep(0.5)
    messagebox.showwarning("Cache Error", "There was a problem creating the cache file \n You can only use the default bundles for now")

def updateActivity() -> None:
    """
    Updates the active status on the server on every 100 seconds, just to know how many actives there are
    """
    while True:
        asyncio.run(sendData('active', active=True, uid=UUID))
        if terminate.is_set():
            break
        sleep(100)

def quitIfNotSupported(window) -> None:
    """
    There will be a text file in the repo, it contains a list of the program versions, if a certin version is not supported/broken then I would 
    be able to force updating for all users

    Args:
        window: tk.Tk() -> used to close the app
    """
    while True:
        if not checkInternetConnection():
            sleep(2)

            validation_status = getVersionValidation(current_version)
            
            if validation_status == True:
                break

            if validation_status == False:
                if not messagebox.askokcancel("Required Update", f"Yemen IPCC version {current_version} \n is no longer supported \n\n Please update to the latest version"):
                    window.withdraw()
                    asyncio.run(sendData('active', active=False, uid=UUID))
                    window.destroy()
                    break
                else:
                    webbrowser.open_new_tab("https://github.com/Abdullah-Albanna/YemenIPCC/releases/latest")
                    window.withdraw()
                    asyncio.run(sendData('active', active=False, uid=UUID))
                    window.destroy()
                    break
        if terminate.is_set():
            break
        sleep(1)




def main() -> None:
    """
    Main executions
    """
    # Used to change the radio button options
    x: tk.IntVar = tk.IntVar()
    y: tk.IntVar = tk.IntVar()

    # Creates the Tk window things with debuging 
    try:
        windowCreation(window)
        logger.debug("Made the window")
    except Exception as e:
        logger.error(f"An error occurred while creating the window, error: {e}")

    # Creates the menu bar option and commands with debuging
    try:
        menuBarCreation(window, current_version, app_font)
        logger.debug("Made the menu bar")
    except Exception as e:
        logger.error(f"An error occurred while creating the menu bar, error: {e}")

    # Creates the label to indicate the device is connected or not
    Stats: tk.Label = tk.Label(window, text="Disconnected", font=(app_font, DPIResize(30)), bg="#0a1750",  # Light Blue > < Dark Blue
                               fg="red",)
    Stats.pack(anchor=tk.NW, side="top", fill="both")

    # Main inject button creation
    button: tk.Button = Button(window,
                    text="Inject",
                    font=(app_font, DPIResize(27), "bold"),
                    relief=tk.RAISED,
                    command=lambda: injection(window, log_text, selected_bundle, selected_container, app_font),
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
        logger.debug("Made the frames")
    except Exception as e:
        logger.error(f"An error occurred while creating the frames, error: {e}")

    # Same thing 
    try:
        radioButtons(which_one, bundles, x, y, app_font)
        logger.debug("Made the radio buttons")
    except Exception as e:
        logger.error(f"An error occurred while creating the radio buttons, error: {e}")

    # Same thing
    try:
        log_text: tk.Text = logText(app_font)
        logger.debug("Made the log text")
    except Exception as e:
        logger.error(f"An error occurred while creating the log text, error: {e}")

    # Necessary threads for the app to function with debuging
    startThread(lambda: disableIfRunning(button, window), "disableIfRunning" )
    startThread(lambda: checkForUpdate(current_version), "checkForUpdate")
    updateButtonStateThreaded(window, frame, button, log_text, Stats)
    updateLabelStateThreaded(window, frame, button, log_text, Stats)
    startThread(getSelectedOption, "getSelectedOption")
    startThread(updateActivity, "updating activity")
    startThread(lambda: quitIfNotSupported(window), "quitIfNotSupported")
    startThread(lambda: asyncio.run(sendData('app opens')), "Send active status")



    # For some reason, I had to put it down here so it would be set down the window
    button.pack(side="bottom", fill="both")


    # Starts the window fixies (sets it to the center)
    try:
        initialize(window)
        logger.debug("Made the initialization of the window")
    except Exception as e:
        logger.error(f"An error occurred while initializing window, error: {e}")

    # This detects if user closed the app from the "x" button on the right top, if so then inform the server that I'm not active anymore
    window.protocol("WM_DELETE_WINDOW", lambda: [window.destroy(), asyncio.run(sendData('active', active=False, uid=UUID)), handleExit()])
    
    # And shows the window, YAY!
    try:
        window.mainloop()
    except KeyboardInterrupt:
        # Hide the window before sending the active false so it won't look forzen
        window.withdraw()
        asyncio.run(sendData('active', active=False, uid=UUID))
        window.quit()
        window.destroy()
        handleExit()

    


if __name__ == "__main__":
    # # If the system is Windows, this will allocate a new console for logging if -d is passed.
    winLogsInit()

    # Register the signal handlers
    signal.signal(signal.SIGINT, handleExit)
    signal.signal(signal.SIGTERM, handleExit)

    # Sets up the logger
    logger = YemenIPCCLogger().logger
    YemenIPCCLogger().run()

    # Creates a new UUID for each run, this is used for the activity updates
    createNewUUID()

    # Initial variables
    UUID = getUUID()
    window: tk.Tk = tk.Tk()
    window.withdraw()
    window.focus()
    try:
        app_font = font.Font(family=getDefaultFont(), size=DPIResize(14) if system == "Mac" or system == "Linux" else DPIResize(10))
    except Exception as e:
        logger.error("Couldn't make the app_font variable")

    tempdir = gettempdir() if system == "Windows" else os.path.join(os.path.expanduser("~/.cache"))
    bundles: List[str] = ["CellularSouthLTE", "USCellularLTE", "China", "ChinaUSIM", "ChinaHK", "CWW"]
    which_one: List[str] = ["default.bundle", "unknown.bundle"]
    logger.debug(f"OS: {platform.platform()}")

    # This is necessary, it changes to the app directory so the app would run normally if you run the script from another directory
    app_directory = getAppDirectory()
    logger.debug(f"App directory is: {app_directory}")
    logger.debug(f"Current directory: {os.getcwd()}")

    # Logs the distro
    if system == "Linux":
        logger.debug(f"Linux Distribution: {platform.freedesktop_os_release().get('PRETTY_NAME')}")
        logger.debug(f"Linux Version: {platform.freedesktop_os_release().get('VERSION')}")

    # If the current running directory is in the macOS bundle app,
    # or there is no folder called "Scripts" in the currrent directory then change the current directory to the executed script directory
    if app_directory.endswith("/Content/MacOS") or not os.path.exists(os.path.join(os.getcwd(), "Scripts")):
        os.chdir(app_directory)
        logger.debug(f"Switched directory to {app_directory}")

    # This will create the file if it doesn't exist or earse the content if it dose
    try:
        if not os.path.exists(os.path.join(tempdir, "yemenipcc")):
            os.mkdir(os.path.join(tempdir, "yemenipcc"))

        with open(os.path.join(tempdir, "yemenipcc", "yemenipcc_temp_variables.txt"), 'w'):
            pass
        logger.debug("Made the chache file")

    except Exception as e:
        logger.error(f"Something went wrong in the making of the chache file, error: {e}")


    # Writes the app version in a __version__ file
    with open(os.path.join(".", "__version__"), 'w') as file:
        file.write(current_version)


    # It just automates the process, to make it easier for noobs
    pattern = os.path.join(".", "Scripts", "*_binary")  # This just takes the binary folders
    matching_folders = glob.glob(pattern) # And this applies the wildcard

    for folder_path in matching_folders:
        if not "windows_binary" in folder_path : # not necessary for windows
            if "mac_binary" in folder_path and system != "Darwin": #  If it detects the mac binary and it is not a mac machine, skip
                continue
            elif "linux_binary" in folder_path and system != "Linux": # Same
                continue
            # Sets the permission
            setExecutePermission(folder_path)

    # Executes the main program
    main()