import locale
from typing import Literal


def getLang() -> Literal["en", "ar"]:
    lang: str = locale.getlocale()[0]

    if not lang:
        lang = "ar"

    if lang.startswith("ar"):
        return "ar"

    else:
        return "en"


def isItArabic() -> bool:
    if getLang() == "ar":
        return True

    else:
        return False
