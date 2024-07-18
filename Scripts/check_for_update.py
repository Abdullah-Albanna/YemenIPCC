from . import (
    messagebox, requests, webbrowser, 
    Union, 
    logger,
    sleep
    )
from .check_for_internet import checkInternetConnection
from .get_system import system

def checkForUpdate(current_version: str, max_length: int = 30) -> Union[bool, str]:
    """
    Check for updates of the YemenIPCCProject app.

    Args:
        current_version (str): The current version of the app.
        max_length (int): Maximum number of lines to display in the message.

    Returns:
        Union[bool, str]: True if an update is available and user chooses to update,
                          False if there is no update available or there's an error fetching updates,
                          "No Internet" if there's no internet connection,
                          "No Update" if there is no new updates.
    """
    if not checkInternetConnection():
        return "No Internet"
    
    sleep(1)
    repo_url = 'https://api.github.com/repos/Abdullah-Albanna/YemenIPCC/releases'
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching update information: {e}")
        return False

    releases_info = response.json()

    for release in releases_info:
        for asset in release["assets"]:
            # Adjusted to match with system in asset name (assuming 'system' is defined somewhere)
            if system in asset['name']:
                latest_version = release['tag_name']
                size = asset['size']
                message = release['body']

                if latest_version == current_version or latest_version < current_version:
                    logger.info("There is no update")
                    return "No Update"
                else:
                    logger.info(f"There is a new update, version: {latest_version}")
                
                # Calculate number of lines in the message
                lines = len(message.splitlines())

                # Crop the message if it exceeds max_length lines
                if lines > max_length:
                    message_lines = '\n'.join(message.splitlines()[:max_length]) + "... Click Yes to Read the Rest"
                else:
                    message_lines = message

                size_mb = round(size / (1024 * 1024), 2)
                update_message = (
                    f"A new version ({latest_version}) is available!\n"
                    f"Do you want to update?\n\n"
                    f"Size: {size_mb} MB\n\n"
                    f"Message:\n{message_lines}"
                )

                if not messagebox.askyesno("Update Available", update_message):
                    logger.info("User declined the update")
                    return False
                
                download_url = release['html_url']
                webbrowser.open_new_tab(download_url)
                logger.info("User accepted the update")
                return True

    return "No Update"
            


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
        messagebox.showinfo("Check for Update", "Yemen IPCC is up-to-date")
    elif update_result == "No Internet":
        messagebox.showerror("Error", "Please connect to the internet first")
