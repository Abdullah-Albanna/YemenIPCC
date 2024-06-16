from .changing_option import (changeWhichOne, changeBundle)
from .check_for_update import (checkForUpdateButton)
from .injection import (cleanRemove)
from .repair import (repairiPhone)
from .thread_starter import startThread
from .variables_manager import VariableManager

from .projectimports import (tk, List, os, system, DPIResize, sleep, webbrowser, messagebox) 
from .logging_config import setupLogging
import logging


setupLogging(debug=True, file_logging=True)

def saveVariableInfo(variable_name, variable_info):
        # Load existing variables from the text file
    try:
        temp_variables = VariableManager().loadTempVariables()
    except Exception as e:
        logging.error(f"updating_status.py - Could not load the saved bundle variables, error: {e}")

    # Update or add the selected bundle name to the saved variables
    temp_variables[f'{variable_name}'] = variable_info
    
    # Save the updated variables to the text file
    try:
        VariableManager().saveVariables(temp_variables)
    except Exception as e:
        logging.error(f"updating_status.py - Could not save bundle option, error: {e}")


def logText(app_font: tk.font) -> tk.Text:

    """
    Creates and configures the log text widget.
    
    Returns:
        tk.Text: The created log text widget.
    """
    global log_text
    # Create log text widget
    try:
        log_text = tk.Text(log_frame, font=(app_font, DPIResize(12)), wrap="word", bg="#0a1750", fg="white", width=35)
        log_text.pack(side=tk.LEFT, fill="both")
    except Exception as e:
        logging.error(f"main_window.py - An error occurred while packing the log_text, error: {e}")

    # Create scrollbar for log text widget
    try:
        log_scrollbar: tk.Scrollbar = tk.Scrollbar(log_frame, command=log_text.yview, width=1, troughcolor="#030b2c")
        log_scrollbar.pack(side=tk.RIGHT, fill="y")
    except Exception as e:
        logging.error(f"main_window.py - An error occurred while packing the log_scrollbar, error: {e}")

    log_text.config(yscrollcommand=log_scrollbar.set)

    return log_text

def radioButtons(which_one: List[str], bundles: List[str], x: tk.IntVar, y: tk.IntVar, app_font: tk.font) -> None:

    """
    Creates radio buttons for selecting which option and bundle to choose.
    
    Args:
        which_one (list): List of options.
        bundles (list): List of bundles.
        x (tk.IntVar): Variable for the bundle selection.
        y (tk.IntVar): Variable for the option selection.
    """
    global selected_bundle, selected_which_one

    # Create radio buttons for options
    for index in range(len(which_one)):  

        radio_which_one_buttom: tk.Radiobutton = tk.Radiobutton(whichoneframe,
                                text=which_one[index],
                                variable=y,
                                value=index,
                                font=(app_font, DPIResize(15)),
                                padx=33,
                                compound="top",
                                indicatoron=1,
                                activebackground="white",
                                bg="#030b2c", # Dark Blue
                                fg="white",
                                selectcolor="#3b56bc", # Light Blue
                                command=lambda: changeWhichOne(log_text, which_one, y),
                                width=10,
                                )
        radio_which_one_buttom.pack(anchor=tk.NE, fill="both")

    # Create radio buttons for bundles
    for index in range(len(bundles)):  

        radio_button: tk.Radiobutton = tk.Radiobutton(selectorframe,
                                text=bundles[index],
                                variable=x,
                                value=index,
                                font=(app_font, DPIResize(20)),
                                padx=33,
                                compound="left",
                                indicatoron=0,
                                activebackground="white",
                                bg="#030b2c", # Dark Blue
                                fg="white",
                                selectcolor="#3b56bc", # Light Blue
                                command=lambda: changeBundle(log_text, bundles, x),
                                width=10,
                                )
        radio_button.pack(anchor=tk.NW, fill="both", expand=True)
    

def ContainerTypeLabel() -> None:

    """
    Creates a label for indicating the type of .ipcc.
    """
    tk.Label(whichoneframe, text="Container Type:", font=("Arial", DPIResize(25)), bg="#030b2c", fg="white").pack(side="top", fill="both")


def frames(window: tk.Tk) -> tk.Frame:

    """
    Creates and configures different frames within the window.
    
    Args:
        window (tk.Tk): The main window.
    
    Returns:
        tk.Frame: The main frame of the window.
    """
    global frame, selectorframe, whichoneframe, log_frame

    # Create frame for bundle and option selection
    selectorframe = tk.Frame(window, bg="#030b2c", bd=3, relief=tk.SUNKEN, padx=20, pady=20)
    selectorframe.pack(anchor=tk.NE, side="right", fill="both")

    # Create frame for option selection
    whichoneframe = tk.Frame(selectorframe, bg="#030b2c", bd=3, relief=tk.SUNKEN, padx=20, pady=20)
    whichoneframe.pack(anchor=tk.NE, side="top", fill="y")

    # Create frame for log display
    log_frame = tk.Frame(window, bg="#030b2c", bd=3, relief=tk.SUNKEN, padx=-200, pady=20)
    log_frame.pack(anchor=tk.NW, side="left", fill="both")

    # Create main frame
    frame = tk.Frame(window, bg="#030b2c", # Dark Blue
                     bd=3, relief=tk.SUNKEN, padx=45, pady=20)
    
    frame.pack(anchor=tk.N, fill="both", side="top")

    ContainerTypeLabel()

    return frame


def windowCreation(window: tk.Tk) -> None:

    """
    Configures the main window.
    
    Args:
        window (tk.Tk): The main window.
    """
    # Gets the resolution of the device and set it to it and subtract from it a little so it won't go full screen
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    logging.debug(f"main_window.py - Screen resolution: {screen_width}:{screen_height}")
    window.geometry(f"{round(screen_width * 0.80)}x{round(screen_height * 0.80)}")


    window.title("Yemen IPCC - by Abdullah Al-Banna")
    window.config(background="#030b2c") # Dark Blue
    path = os.path.join("_internal", "Scripts", "Images", "YemenIPCC.png")
    if os.path.exists(path):
        icon = tk.PhotoImage(file=path)
    else:
        icon = tk.PhotoImage(file=os.path.join("." ,"Scripts", "Images", "YemenIPCC.png"))

    window.iconphoto(True, icon)
    window.withdraw() 
    
def menuBarCreation(window: tk.Tk, current_version: str, app_font: tk.font) -> None:

    def on_validate_toggle():
        if validate_var.get():
            saveVariableInfo("validate", "True")
        else:
            if messagebox.askyesno("Disable Validation", "Turning off validating would make development slow, it is recommended to leave it on\n\n Are you sure you want to disable it?"):
                saveVariableInfo("validate", "False")
            else:
                validate_var.set(True)
    """
    Creates and configures the menu bar.
    
    Args:
        window (tk.Tk): The main window.
        current_version (str): The current version of the project.
    """

    menubar = tk.Menu(window)
    window.config(menu=menubar, bg="#0a1750") # Lighter than the Dark Blue
    validate_var = tk.BooleanVar(value=True)  # Checked by default
    

    mainmenu = tk.Menu(menubar, tearoff=0, font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)))
    toolsmenu = tk.Menu(menubar, tearoff=0, font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)))
    helpmenu = tk.Menu(menubar, tearoff=0, font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)))
    

    # It looks bad in Macs :(
    if system != "Mac":
        menubar.add_cascade(label="Main", menu=mainmenu, font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)))
        mainmenu.add_command(label="exit", font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)), command=window.quit)

    menubar.add_cascade(label="Tools", menu=toolsmenu, font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)))
    toolsmenu.add_command(label="clean", font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)), command=lambda: cleanRemove(window, log_text, app_font))
    toolsmenu.add_command(label="re-pair", font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)), command=lambda: repairiPhone(log_text))
    # Add a checkbutton to the Tools menu
    toolsmenu.add_checkbutton(
        label="validate",
        font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)),
        variable=validate_var,
        command=on_validate_toggle
    )

    toolsmenu.add_separator()
    toolsmenu.add_command(label="check for updates", font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)), command=lambda: checkForUpdateButton(current_version))

    menubar.add_cascade(label="Help", menu=helpmenu, font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)))
    helpmenu.add_command(label="github", font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)), command=lambda: webbrowser.open_new_tab("https://github.com/Abdullah-Albanna/YemenIPCC"))
    if system != "Mac":
        helpmenu.add_separator()
        helpmenu.add_command(label="about", font=(app_font, 14 if system == "Mac" or system == "Linux" else DPIResize(10)), command= lambda: messagebox.showinfo("About", f"Yemen IPCC \n\n A simple app to automate the process of injecting the network configuration files (.ipcc) to the iPhone devices in Yemen\n\n\n author: Abdullah Al-Banna \n version: {current_version}"))