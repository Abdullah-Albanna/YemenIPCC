from Scripts.check_for_update import (checkForUpdate)
from Scripts.fixing_the_window import (initialize)
from Scripts.changing_option import (VariableManager)
from Scripts.injection import (injection, disableIfRunning)
from Scripts.updating_status import (updateButtonStateThreaded, updateLabelStateThreaded)
from Scripts.main_window import (logText, radioButtons, frames, windowCreation, menuBarCreation)

from Scripts.projectimports import (tk, List, Thread, os, sleep, gettempdir, platform, getAppDirectory, family_font, font, DPIResize)


current_version: str = "v1.0.0"



# Gets the current selected option from the the temp file
def getSelectedOption() -> None:
    global selected_bundle, selected_which_one

    while True:
        saved_variables = VariableManager().loadSavedVariables()
        selected_bundle = saved_variables.get('selected_bundle', 'CellularSouthLTE')
        selected_which_one = saved_variables.get('selected_which_one', 'Default.bundle')
        sleep(0.5)
    

def main() -> None:

    # Used to change the radio button options
    x: tk.IntVar = tk.IntVar()
    y: tk.IntVar = tk.IntVar()

    # Creates the Tk window things
    windowCreation(window)
    # Creates the menu bar option and commands
    menuBarCreation(window, current_version, app_font)

    # Creates the label to indicate the device is connected or not
    Stats: tk.Label = tk.Label(window, text="Disconnected", font=(app_font, DPIResize(30)), bg="#0a1750",  # Light Blue > < Dark Blue
                               fg="red",)
    Stats.pack(anchor=tk.NW, side="top", fill="both")

    # Main inject button creation
    button: tk.Button = tk.Button(window,
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
                    state=tk.DISABLED)
    

    # Sets the individual frames and set it to a variable to be used for other functions
    frame: tk.Frame = frames(window)

    radioButtons(which_one, bundles, x, y, app_font)

    # Same thing, creates the log text 
    log_text: tk.Text = logText(app_font)

    # Necessary threads for the app to function
    Thread(target=lambda: disableIfRunning(button, window), daemon=True).start()
    Thread(target=lambda: checkForUpdate(current_version), daemon=True).start()    
    Thread(target=lambda: updateButtonStateThreaded(window, frame, button, log_text, Stats), daemon=True).start()
    Thread(target=lambda: updateLabelStateThreaded(window, frame, button, log_text, Stats), daemon=True).start()
    Thread(target=getSelectedOption, daemon=True).start()

    # For some reason, I had to put it down here so it would be set down the window
    button.pack(anchor=tk.SE, side="bottom", fill="both")

    # Starts the window fixies (sets it to the center)
    initialize(window)

    # And shows the window, YAY!
    window.mainloop()
    




if __name__ == "__main__":

    # Initial variables
    system = platform.system()
    window: tk.Tk = tk.Tk()
    window.focus()
    app_font = font.Font(family=family_font, size=DPIResize(14) if system == "Mac" or system == "Linux" else DPIResize(10))
    bundles: List[str] = ["CellularSouthLTE", "USCellularLTE", "China", "ChinaUSIM", "ChinaHK", "CWW"]
    which_one: List[str] = ["Default.bundle", "Unknown.bundle"]
    tempdir = gettempdir() if system == "Windows" else os.path.expanduser("~/.cache")


    app_directory = getAppDirectory()

    # If the current running directory is in the macOS bundle app,
    # or there is no folder called "Scripts" in the currrent directory then change the current directory to the executed script directory
    if app_directory.endswith("/Content/MacOS") or not os.path.exists(os.path.join(os.getcwd(), "Scripts")):
        target_directory = app_directory
        os.chdir(target_directory)

    # This will create the file if it doesn't exist or earse the content if it does
    with open(os.path.join(tempdir, "saved_variables.txt"), 'w'):
        pass



    main()