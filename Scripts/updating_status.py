from .projectimports import (tk, sleep, Thread, Tuple, Dict, List, subprocess, platform, os, cache)
from .changing_option import VariableManager

dsystem = platform.system()

# Used to change the "Darwin" to "Mac" because it is known better in Mac not Darwin
if dsystem == "Darwin":
    system: str = "Mac"
else:
    system = dsystem
    
# What these three do is specifing the executeable binary for each system so the user do not have to install anything
if system == "Mac":

    os.environ['DYLD_LIBRARY_PATH'] = "./Scripts/mac_binary/lib:$DYLD_LIBRARY_PATH"
    env = os.environ.copy()

    ideviceinfo: str = "./Scripts/mac_binary/ideviceinfo"
    idevice_id: str = "./Scripts/mac_binary/idevice_id"
    idevicepair: str = "./Scripts/mac_binary/idevicepair"


if system == "Linux":

    os.environ['LD_LIBRARY_PATH'] = "./Scripts/linux_binary/lib"
    env = os.environ.copy()

    ideviceinfo: str = "./Scripts/linux_binary/ideviceinfo" 
    idevice_id: str = "./Scripts/linux_binary/idevice_id"
    idevicepair: str = "./Scripts/linux_binary/idevicepair"

elif system == "Windows":

    ideviceinfo: str = ".\\Scripts\\windows_binary\\ideviceinfo.exe" 
    idevice_id: str = ".\\Scripts\\windows_binary\\idevice_id.exe"
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



@cache
def cachedDPIAndRes():
    window = tk.Tk()
    dpi = window.winfo_fpixels('1i')
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.destroy()
    return dpi, screen_width

def DPIResize(size) -> int:
    """Get the screen DPI and screen resolution using Tkinter, and convert the font size to be suitable for it"""
    if system == "Mac":
        # Macs are known to use 72
        sysdpi = 72
    else:
        sysdpi = 96
    dpi, screen_width = cachedDPIAndRes()\
    
    if 1366 <= screen_width < 1600:
        sysdpi+=12
    elif 1280 <= screen_width < 1366:
        sysdpi+=23
    elif 1024 <= screen_width < 1280:
        sysdpi+=50

    scale_factor = dpi / sysdpi
    return round(int(size * scale_factor))


    
# A class to control the iPhone
class DeviceManager:
    def __init__(self, window=None, frame=None, button=None, log_text=None, Stats=None):
        self.window: tk.Tk = window
        self.frame: tk.Frame = frame
        self.button: tk.Button = button
        self.log_text: tk.Text = log_text
        self.Stats: tk.Label = Stats
        self.iPhoneType: tk.Label = None
        self.iPhoneVersion: tk.Label = None
        self.disconnected_label: tk.Label = None
        # self.app_font = app_font
    
    # Check if the device is really paired 
    def validateDevice(self) -> bool:
        try:
            # Runs ideviceinfo, which is used to get the iPhone information, and catch the errors, if there is no, then it is good to go
            subprocess.Popen([ideviceinfo], **args)
            return True
        except subprocess.CalledProcessError as e:
            error_message: str = e.stderr.strip()
            if "Could not connect to lockdownd: SSL error (-5)" in error_message:
                return False
            elif "Device validation failed: unhandled error code -5" in error_message:
                self.Stats.config(text="Please Reconnect the USB and Trust Again", fg="red")
                return False
            

    # Extracts some information about the connected device
    def extractValuesFromLog(self) -> Tuple[int, str]:
        product_version: int = ""
        product_type: str = ""
        try:
            # -s is short for "short", maybe
            device_info = subprocess.Popen([ideviceinfo, "-s"], **args)
            stdout = device_info.communicate()[0]
            stderr = device_info.communicate()[1]
            output_lines: List[str] = stdout.splitlines() + stderr.splitlines()

            # This one look for the iPhone type and its version, and saves it to the above variables
            for line in output_lines:
                if "ProductVersion:" in line:
                    product_version = line.split("ProductVersion:")[1].strip() # The "1" if for the whitespace
                elif "ProductType:" in line:
                    product_type = line.split("ProductType:")[1].strip()

            # Creating a dictionary to convert machine id to a known name, used then for displaying what iPhone is connected 
            product_type_mappings: Dict[str, str] = {
                'iPhone7,2': "iPhone 6",
                'iPhone7,1': "iPhone 6+",
                'iPhone8,1': "iPhone 6S",
                'iPhone8,2': "iPhone 6S+",
                'iPhone8,4': "iPhone SE.2016",
                'iPhone9,1': "iPhone 7",
                'iPhone9,2': "iPhone 7 Plus",
                'iPhone10,1': "iPhone 8",
                'iPhone10,2': "iPhone 8 Plus",
                'iPhone10,3': "iPhone X",
                'iPhone11,2': "iPhone XS",
                'iPhone11,4': "iPhone XS Max.China",
                'iPhone11,6': "iPhone XS Max",
                'iPhone11,8': "iPhone XR",
                'iPhone12,1': "iPhone 11",
                'iPhone12,3': "iPhone 11 Pro",
                'iPhone12,5': "iPhone 11 Pro Max",
                'iPhone12,8': "iPhone SE.2020",
                'iPhone13,1': "iPhone 12 Mini",
                'iPhone13,2': "iPhone 12",
                'iPhone13,3': "iPhone 12 Pro",
                'iPhone13,4': "iPhone 12 Pro Max",
                'iPhone14,4': "iPhone 13 Mini",
                'iPhone14,5': "iPhone 13",
                'iPhone14,2': "iPhone 13 Pro",
                'iPhone14,3': "iPhone 13 Pro Max",
                'iPhone14,6': "iPhone SE.2022"
            }

            product_type = product_type_mappings.get(product_type, "Unsupported")

        except subprocess.CalledProcessError:
            # Catching the error of the ideviceinfo, if it has errors then it is probably not trusted
            self.log_text.tag_configure("red", foreground="red")
            self.log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
            self.log_text.insert(tk.END, f"\nCommand 'ideviceinfo -s' returned non-zero exit status\n", "red")
            self.Stats.config(text="Please Trust this Computer", fg="green")
            subprocess.Popen([f"{idevicepair}", "pair"], **args)

        return product_version, product_type

    # Checks if the device is plugged or not
    def checkIfPlugged(self) -> bool:
        try:
            # This prints the iPhone id, whether it is trusted or not, which is good, we only want to know if it plugged or not
            result = subprocess.Popen([idevice_id, "-l"], **args)
            stdout = result.communicate()[0]
            return bool(stdout.strip())
        except subprocess.CalledProcessError as e:
            return False
        

    # Updates the button state, if the device is plugged it gets enabled, if not then no, if plugged and the injection is running then no
    def updateButtonState(self) -> None:
        while True:
            plugged = self.checkIfPlugged()
            running = self.getRunningStatus()

            if running and plugged:
                self.button.config(state=tk.DISABLED)
            elif not running:
                self.button.config(state=tk.NORMAL if plugged else tk.DISABLED)
            sleep(0.3)
            self.window.update_idletasks()


    # Same thing, but a bit more
    def updateLabelState(self) -> None:
        while True:
            plugged = self.checkIfPlugged()

            # if it is plugged and returns False on the validation, we need to trust the device
            if not self.validateDevice() and plugged:
                self.log_text.tag_configure("red", foreground="red")
                self.log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
                self.log_text.insert(tk.END, f"\nDevice validation failed: unhandled error code -5\n", "red")
                self.Stats.config(text="Please Reconnect the USB and Trust", fg="red")
                sleep(1)
                subprocess.Popen([f'{idevicepair}', 'pair'], **args)
                sleep(1)

            if plugged:
                self.Stats.config(text="Connected", fg="green")

                # We don not want thoes to be global from the extractValuesFromLog because we need to to repeatedly know what device is connected
                product_version, product_type = self.extractValuesFromLog()

                # Because this function is in a while loop, we need a way of handling the labels from repeating and going on a long line 
                if not self.iPhoneType: # This is like if the label is not empty, clear it
                    self.iPhoneType = tk.Label(self.frame, font=("Consolas", DPIResize(18)), bg="#030b2c", fg="white")
                    self.iPhoneType.pack()
                self.iPhoneType.config(text=f"iPhone Type: {product_type}") # Then fill it again

                if not self.iPhoneVersion: # Same and so as the other
                    self.iPhoneVersion = tk.Label(self.frame, font=("Consolas", DPIResize(20)), bg="#030b2c", fg="white")
                    self.iPhoneVersion.pack()
                self.iPhoneVersion.config(text=f"iPhone Version: {product_version}")

                if self.disconnected_label:
                    self.disconnected_label.pack_forget()
                    self.disconnected_label = None
            else:
                self.Stats.config(text="Disconnected", fg="red")                       # Same logic 
                if self.iPhoneType:
                    self.iPhoneType.pack_forget()
                    self.iPhoneType = None
                if self.iPhoneVersion:
                    self.iPhoneVersion.pack_forget()
                    self.iPhoneVersion = None

                if not self.disconnected_label:
                    self.disconnected_label = tk.Label(self.frame, text="Please connect your iPhone", font=("Consolas", DPIResize(20)), bg="#030b2c", fg="white")
                    self.disconnected_label.pack() #Consolas

            sleep(0.3)
            self.window.update_idletasks() # And finally updates the window
            
    def getRunningStatus(self) -> bool:
        saved_variables = VariableManager().loadSavedVariables()
        running = saved_variables.get('running', 'False')
        if running == "False":
            return False
        elif running == "True":
            return True
                


# Both has to be running from here, if you don't, you'll get weird behavior
def updateButtonStateThreaded(window: tk.Tk, frame: tk.Frame, button: tk.Button, log_text: tk.Text, Stats: tk.Label) -> None:
    Thread(target=lambda: DeviceManager(window, frame, button, log_text, Stats).updateButtonState(), daemon=True).start()
    

def updateLabelStateThreaded(window: tk.Tk, frame: tk.Frame, button: tk.Button, log_text: tk.Text, Stats: tk.Label) -> None:
    Thread(target=lambda: DeviceManager(window, frame, button, log_text, Stats).updateLabelState(), daemon=True).start()