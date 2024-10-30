import webbrowser
from time import sleep


from database.db import DataBase
from config.secrets import Env
from utils.messageboxes import MessageBox

from checkers.check_for_internet import checkInternetConnection
from checkers.check_version_validation import getVersionValidation
from handles.send_data import sendData
from utils.get_os_lang import isItArabic

from thread_management.thread_terminator_var import terminate

arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]


def quitIfNotSupported(window, current_version, UUID) -> None:
    """
    There will be a text file in the repo, it contains a list of the program versions, if a certin version is not
    supported/broken then I would be able to force updating for all users

    Args:
        window: tk.Tk() -> used to close the app
        current_version: str -> the apps version
        UUID: uuid.UUID4 -> used to differentiate between users
    """
    while True:
        if not checkInternetConnection():
            sleep(2)

            validation_status = getVersionValidation(current_version)

            if validation_status is True:
                break

            if validation_status is False:
                if not MessageBox().askokcancel(
                    "Required Update",
                    (
                        f" Yemen IPCC {current_version} \n\n لم يعد مدعومًا \n\n يرجى التحديث إلى أحدث إصدار"
                        if arabic
                        else f"Yemen IPCC version {current_version} \n is no longer supported \n\n Please update to the latest version"
                    ),
                ):
                    window.withdraw()
                    sendData("active", active=False, uid=UUID)
                    window.destroy()
                    break
                else:
                    webbrowser.open_new_tab(
                        f"https://github.com/{Env().repo}/releases/latest"
                    )
                    window.withdraw()
                    sendData("active", active=False, uid=UUID)
                    window.destroy()
                    break
        if terminate.is_set():
            break
        sleep(1)
