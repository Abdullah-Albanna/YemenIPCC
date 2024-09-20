import tkinter as tk
from typing import List

from ..database.db import DataBase
from ..utils.logger_config_class import YemenIPCCLogger
from ..utils.get_os_lang import isItArabic

from ..arabic_tk.bidid import renderBiDiText

arabic = DataBase.get(["arabic"], [isItArabic()], "app")[0]
logger = YemenIPCCLogger().logger


def changeBundle(
        log_text: tk.Text | None = None,
        bundles: List[str] | None = None,
        x: tk.IntVar | None = None,
) -> str:
    """
    Update the selected bundle based on the user's choice and display a message in the log text.

    Args:
        log_text (tk.Text): The text widget to display log messages.
        bundles (List[str]): List of bundle names.
        x (tk.IntVar): The variable representing the selected bundle index.

    Returns:
        str: The selected bundle name.
    """

    # Gets what you selected
    selected_bundle = bundles[x.get()]
    logger.debug(f"Selected a new bundle option: {selected_bundle}")
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(
            tk.END,
            (
                renderBiDiText(f"\n{selected_bundle} تم اختيار \n")
                if arabic
                else f"\nSelected {selected_bundle}\n"
            ),
        )
        log_text.see(tk.END)

    DataBase.add(["selected_bundle"], [selected_bundle], "bundle")

    return selected_bundle


def changeWhichOne(
        log_text: tk.Text | None = None,
        which_one: List[str] | None = None,
        y: tk.IntVar | None = None,
) -> str:
    """
    Update the selected 'which one' option based on the user's choice and display a message in the log text.

    Args:
        log_text (tk.Text): The text widget to display log messages.
        which_one (List[str]): List of 'which one' options.
        y (tk.IntVar): The variable representing the selected 'which one' index.

    Returns:
        str: The selected 'which one' option.
    """
    selected_container = which_one[y.get()]
    logger.debug(f"Selected a new container option: {selected_container}")
    if log_text is not None:
        log_text.insert(tk.END, "⸻⸻⸻⸻⸻⸻⸻")
        log_text.insert(
            tk.END,
            (
                renderBiDiText(f"\n{selected_container} تم اختيار \n")
                if arabic
                else f"\nSelected {selected_container}\n"
            ),
        )
        log_text.see(tk.END)

    DataBase.add(["selected_container"], [selected_container], "bundle")

    return selected_container
