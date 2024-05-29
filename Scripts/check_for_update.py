from .projectimports import (sleep, messagebox, requests, webbrowser,
                            Union, socket, system)


def checkInternetConnection() -> bool:
    """
    Check internet connection by creating a socket connection to a well-known IP address.

    Returns:
        bool: True if internet connection is available, False otherwise.
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        pass
    return False

def checkForUpdate(current_version: str) -> Union[bool, str]:
    """
    Check for updates of the YemenIPCCProject app.

    Args:
        current_version (str): The current version of the app.
    Returns:
        Union[bool, str]: True if an update is available and user chooses to update,
        
                          False if there is no update available or there's an error fetching updates,

                          "No Internet" if there's no internet connection.

                          "No Update" if there is no new updates
    """
    if not checkInternetConnection():
        return "No Internet"
    
    sleep(1)
    repo_url: str = 'https://api.github.com/repos/Abdullah-Albanna/YemenIPCC/releases'
    response = requests.get(repo_url)
    response.raise_for_status()

    releases_info: list = response.json()

    # Checks if there is an update for the current device using the github api, not the best way to write, but alright
    for release in releases_info:
        for asset in release["assets"]:

            if system in asset['name']:
                latest_version: str = release['tag_name']
                size: int = asset['size']
                message: str = release['body']

                if latest_version == current_version:
                    return "No Update"
                
                size_mb: int = round(size / (1024 * 1024), 2)
                update_message = (
                    f"A new version ({latest_version}) is available!\n"
                    f"Do you want to update?\n\n"
                    f"Size: {str(size_mb)} MB\n\n"
                    f"Message:\n{message}"
                )

                if not messagebox.askyesno("Update Available", update_message):
                    return False
                
                download_url: str = release['html_url']
                webbrowser.open_new_tab(download_url)
                return True
            


def checkForUpdateButton(current_version: str) -> None:
    """
    This is mainly for the tools -> check for update button.
    
    Args:
        current_version (str): The current version of the app.
    Returns:
        None
    """
    update_result = checkForUpdate(current_version)
    if update_result == "No Update":
        messagebox.showinfo("Check for Update", "Yemen IPCC app is up-to-date")
    elif update_result == "No Internet":
        messagebox.showerror("Error", "Please connect to the internet first")
