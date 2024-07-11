# Yemen IPCC

This project aims to resolve the issue with old YemenMobile SIMs on iPhones.

Each time there is a new iOS update, YemenMobile SIMs get bricked, and the only solution is to inject a certain network configuration file (.ipcc) into the iPhone to make the SIM work again. This project provides the necessary files and an app to automate that process.

## Note:
$${\color{red}PLEASE \space READ}$$
This project aims to enable calling. 4G might and might not work! Additionally, it works great with American devices and might and might not work for others.

$${\color{green}PLEASE \space CONTRIBUTE \space IF \space YOU \space KNOW \space BETTER!}$$

## How, Who, and Why?

This project uses a macOS machine located in a **different** country and a Python script created by ***me*** to automate the process. I created this project to eliminate the need to visit any store to get your iPhone cellular working and possibly save money.

# Automatically

1. Download the latest app version for your platform from the [releases](https://github.com/Abdullah-Albanna/YemenIPCC/releases) and install it.
2. Open the app and connect your iPhone via USB. You should see **Connected** at the top of the app.
3. Once you verify it is connected, press the **Inject** button to start the process.
4. Wait until it's done.

**[NOTE: If you encounter any problems, please open an issue.]**

# Manually

### How to Get the File

1. Go to the code section, find your iPhone device, and select your iOS version.
2. Choose "Using Default Bundle" (or the other one, whichever works for you).
3. Start downloading from the **download** button or **raw** link.
4. Download the files and move on to the next step: [Using the File](https://github.com/Abdullah-Albanna/YemenIPCCProject/edit/master/README.md#using-the-file).

### Using the File

**Prerequisites:**
- A Windows machine.
- [3uTools](http://www.3u.com/), which will prompt to download **iTunes** if it is not installed; let it do its thing.
- A data-supporting Lightning Cable.
- An iPhone.

**Steps:**
1. Once everything is ready, start 3uTools and ensure your phone is showing.
2. Go to the ToolBox → Install IPCC.

# FAQ

**Do I get money from this project?**
- NO! I do not receive any money, nor do I pay. The server is completely free, thanks to [SegFault](https://www.thc.org/segfault/).

**Is the app safe?**
- YES, the app is open source, meaning you can see exactly what it does if you understand Python, check it out in [here](https://github.com/Abdullah-Albanna/YemenIPCC/tree/app-source).

# Contributing Guidelines

There are no strict rules. You can contribute and submit a pull request if you:
- Have a new and improved method for injecting the files.
- Have a better and more efficient way to write the code.
- Can enhance the UI/UX.
- Know how to get the .ipcc files better.

# Special Thanks

- **[Skyper at SegFault](https://www.thc.org/segfault/)**: Provided a free server.
- **[libimobiledevice](https://github.com/libimobiledevice)**: An open-source project to interact with iPhones and iPads.
