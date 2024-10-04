"""
AwesomeTkinter, a new tkinter widgets design using custom styles and images

:copyright: (c) 2020-2021 by Mahmoud Elshahat.

module description:
    handle arabic text to be shown properly in tkinter widgets
    it works on linux, and windows.

"""

import os
import platform
import tkinter as tk
import re
from bidi import get_display

if not __package__:
    __package__ = "awesometkinter"

from .menu import RightClickMenu

UNSHAPED = 0
ISOLATED = 1
INITIAL = 2
MEDIAL = 3
FINAL = 4

operating_system = (
    platform.system()
)  # current operating system  ('Windows', 'Linux', 'Darwin')

shapes_table = (
    ("\u0621", "\ufe80", "", "", ""),  # (ء, ﺀ, , , ),
    ("\u0622", "\ufe81", "", "", "\ufe82"),  # (آ, ﺁ, , , ﺂ),
    ("\u0623", "\ufe83", "", "", "\ufe84"),  # (أ, ﺃ, , , ﺄ),
    ("\u0624", "\ufe85", "", "", "\ufe86"),  # (ؤ, ﺅ, , , ﺆ),
    ("\u0625", "\ufe87", "", "", "\ufe88"),  # (إ, ﺇ, , , ﺈ),
    ("\u0626", "\ufe89", "\ufe8b", "\ufe8c", "\ufe8a"),  # (ئ, ﺉ, ﺋ, ﺌ, ﺊ),
    ("\u0627", "\ufe8d", "", "", "\ufe8e"),  # (ا, ﺍ, , , ﺎ),
    ("\u0628", "\ufe8f", "\ufe91", "\ufe92", "\ufe90"),  # (ب, ﺏ, ﺑ, ﺒ, ﺐ),
    ("\u0629", "\ufe93", "", "", "\ufe94"),  # (ة, ﺓ, , , ﺔ),
    ("\u062a", "\ufe95", "\ufe97", "\ufe98", "\ufe96"),  # (ت, ﺕ, ﺗ, ﺘ, ﺖ),
    ("\u062b", "\ufe99", "\ufe9b", "\ufe9c", "\ufe9a"),  # (ث, ﺙ, ﺛ, ﺜ, ﺚ),
    ("\u062c", "\ufe9d", "\ufe9f", "\ufea0", "\ufe9e"),  # (ج, ﺝ, ﺟ, ﺠ, ﺞ),
    ("\u062d", "\ufea1", "\ufea3", "\ufea4", "\ufea2"),  # (ح, ﺡ, ﺣ, ﺤ, ﺢ),
    ("\u062e", "\ufea5", "\ufea7", "\ufea8", "\ufea6"),  # (خ, ﺥ, ﺧ, ﺨ, ﺦ),
    ("\u062f", "\ufea9", "", "", "\ufeaa"),  # (د, ﺩ, , , ﺪ),
    ("\u0630", "\ufeab", "", "", "\ufeac"),  # (ذ, ﺫ, , , ﺬ),
    ("\u0631", "\ufead", "", "", "\ufeae"),  # (ر, ﺭ, , , ﺮ),
    ("\u0632", "\ufeaf", "", "", "\ufeb0"),  # (ز, ﺯ, , , ﺰ),
    ("\u0633", "\ufeb1", "\ufeb3", "\ufeb4", "\ufeb2"),  # (س, ﺱ, ﺳ, ﺴ, ﺲ),
    ("\u0634", "\ufeb5", "\ufeb7", "\ufeb8", "\ufeb6"),  # (ش, ﺵ, ﺷ, ﺸ, ﺶ),
    ("\u0635", "\ufeb9", "\ufebb", "\ufebc", "\ufeba"),  # (ص, ﺹ, ﺻ, ﺼ, ﺺ),
    ("\u0636", "\ufebd", "\ufebf", "\ufec0", "\ufebe"),  # (ض, ﺽ, ﺿ, ﻀ, ﺾ),
    ("\u0637", "\ufec1", "\ufec3", "\ufec4", "\ufec2"),  # (ط, ﻁ, ﻃ, ﻄ, ﻂ),
    ("\u0638", "\ufec5", "\ufec7", "\ufec8", "\ufec6"),  # (ظ, ﻅ, ﻇ, ﻈ, ﻆ),
    ("\u0639", "\ufec9", "\ufecb", "\ufecc", "\ufeca"),  # (ع, ﻉ, ﻋ, ﻌ, ﻊ),
    ("\u063a", "\ufecd", "\ufecf", "\ufed0", "\ufece"),  # (غ, ﻍ, ﻏ, ﻐ, ﻎ),
    (
        "\u0640",
        "\u0640",
        "\u0640",
        "\u0640",
        "\u0640",
    ),  # (ـ, ـ, ـ, ـ, ـ),  Arabic Tatweel
    ("\u0641", "\ufed1", "\ufed3", "\ufed4", "\ufed2"),  # (ف, ﻑ, ﻓ, ﻔ, ﻒ),
    ("\u0642", "\ufed5", "\ufed7", "\ufed8", "\ufed6"),  # (ق, ﻕ, ﻗ, ﻘ, ﻖ),
    ("\u0643", "\ufed9", "\ufedb", "\ufedc", "\ufeda"),  # (ك, ﻙ, ﻛ, ﻜ, ﻚ),
    ("\u0644", "\ufedd", "\ufedf", "\ufee0", "\ufede"),  # (ل, ﻝ, ﻟ, ﻠ, ﻞ),
    ("\u0645", "\ufee1", "\ufee3", "\ufee4", "\ufee2"),  # (م, ﻡ, ﻣ, ﻤ, ﻢ),
    ("\u0646", "\ufee5", "\ufee7", "\ufee8", "\ufee6"),  # (ن, ﻥ, ﻧ, ﻨ, ﻦ),
    ("\u0647", "\ufee9", "\ufeeb", "\ufeec", "\ufeea"),  # (ه, ﻩ, ﻫ, ﻬ, ﻪ),
    ("\u0648", "\ufeed", "", "", "\ufeee"),  # (و, ﻭ, , , ﻮ),
    # ('\u0649', '\uFEEF', '\uFBE8', '\uFBE9', '\uFEF0'),  # (ى, ﻯ, ﯨ, ﯩ, ﻰ),
    ("\u0649", "\ufeef", "", "", "\ufef0"),  # (ى, ﻯ, , , ﻰ),
    ("\u064a", "\ufef1", "\ufef3", "\ufef4", "\ufef2"),  # (ي, ﻱ, ﻳ, ﻴ, ﻲ),
    ("\u0671", "\ufb50", "", "", "\ufb51"),  # (ٱ, ﭐ, , , ﭑ),
    ("\u0677", "\ufbdd", "", "", ""),  # (ٷ, ﯝ, , , ),
    ("\u0679", "\ufb66", "\ufb68", "\ufb69", "\ufb67"),  # (ٹ, ﭦ, ﭨ, ﭩ, ﭧ),
    ("\u067a", "\ufb5e", "\ufb60", "\ufb61", "\ufb5f"),  # (ٺ, ﭞ, ﭠ, ﭡ, ﭟ),
    ("\u067b", "\ufb52", "\ufb54", "\ufb55", "\ufb53"),  # (ٻ, ﭒ, ﭔ, ﭕ, ﭓ),
    ("\u067e", "\ufb56", "\ufb58", "\ufb59", "\ufb57"),  # (پ, ﭖ, ﭘ, ﭙ, ﭗ),
    ("\u067f", "\ufb62", "\ufb64", "\ufb65", "\ufb63"),  # (ٿ, ﭢ, ﭤ, ﭥ, ﭣ),
    ("\u0680", "\ufb5a", "\ufb5c", "\ufb5d", "\ufb5b"),  # (ڀ, ﭚ, ﭜ, ﭝ, ﭛ),
    ("\u0683", "\ufb76", "\ufb78", "\ufb79", "\ufb77"),  # (ڃ, ﭶ, ﭸ, ﭹ, ﭷ),
    ("\u0684", "\ufb72", "\ufb74", "\ufb75", "\ufb73"),  # (ڄ, ﭲ, ﭴ, ﭵ, ﭳ),
    ("\u0686", "\ufb7a", "\ufb7c", "\ufb7d", "\ufb7b"),  # (چ, ﭺ, ﭼ, ﭽ, ﭻ),
    ("\u0687", "\ufb7e", "\ufb80", "\ufb81", "\ufb7f"),  # (ڇ, ﭾ, ﮀ, ﮁ, ﭿ),
    ("\u0688", "\ufb88", "", "", "\ufb89"),  # (ڈ, ﮈ, , , ﮉ),
    ("\u068c", "\ufb84", "", "", "\ufb85"),  # (ڌ, ﮄ, , , ﮅ),
    ("\u068d", "\ufb82", "", "", "\ufb83"),  # (ڍ, ﮂ, , , ﮃ),
    ("\u068e", "\ufb86", "", "", "\ufb87"),  # (ڎ, ﮆ, , , ﮇ),
    ("\u0691", "\ufb8c", "", "", "\ufb8d"),  # (ڑ, ﮌ, , , ﮍ),
    ("\u0698", "\ufb8a", "", "", "\ufb8b"),  # (ژ, ﮊ, , , ﮋ),
    ("\u06a4", "\ufb6a", "\ufb6c", "\ufb6d", "\ufb6b"),  # (ڤ, ﭪ, ﭬ, ﭭ, ﭫ),
    ("\u06a6", "\ufb6e", "\ufb70", "\ufb71", "\ufb6f"),  # (ڦ, ﭮ, ﭰ, ﭱ, ﭯ),
    ("\u06a9", "\ufb8e", "\ufb90", "\ufb91", "\ufb8f"),  # (ک, ﮎ, ﮐ, ﮑ, ﮏ),
    ("\u06ad", "\ufbd3", "\ufbd5", "\ufbd6", "\ufbd4"),  # (ڭ, ﯓ, ﯕ, ﯖ, ﯔ),
    ("\u06af", "\ufb92", "\ufb94", "\ufb95", "\ufb93"),  # (گ, ﮒ, ﮔ, ﮕ, ﮓ),
    ("\u06b1", "\ufb9a", "\ufb9c", "\ufb9d", "\ufb9b"),  # (ڱ, ﮚ, ﮜ, ﮝ, ﮛ),
    ("\u06b3", "\ufb96", "\ufb98", "\ufb99", "\ufb97"),  # (ڳ, ﮖ, ﮘ, ﮙ, ﮗ),
    ("\u06ba", "\ufb9e", "", "", "\ufb9f"),  # (ں, ﮞ, , , ﮟ),
    ("\u06bb", "\ufba0", "\ufba2", "\ufba3", "\ufba1"),  # (ڻ, ﮠ, ﮢ, ﮣ, ﮡ),
    ("\u06be", "\ufbaa", "\ufbac", "\ufbad", "\ufbab"),  # (ھ, ﮪ, ﮬ, ﮭ, ﮫ),
    ("\u06c0", "\ufba4", "", "", "\ufba5"),  # (ۀ, ﮤ, , , ﮥ),
    ("\u06c1", "\ufba6", "\ufba8", "\ufba9", "\ufba7"),  # (ہ, ﮦ, ﮨ, ﮩ, ﮧ),
    ("\u06c5", "\ufbe0", "", "", "\ufbe1"),  # (ۅ, ﯠ, , , ﯡ),
    ("\u06c6", "\ufbd9", "", "", "\ufbda"),  # (ۆ, ﯙ, , , ﯚ),
    ("\u06c7", "\ufbd7", "", "", "\ufbd8"),  # (ۇ, ﯗ, , , ﯘ),
    ("\u06c8", "\ufbdb", "", "", "\ufbdc"),  # (ۈ, ﯛ, , , ﯜ),
    ("\u06c9", "\ufbe2", "", "", "\ufbe3"),  # (ۉ, ﯢ, , , ﯣ),
    ("\u06cb", "\ufbde", "", "", "\ufbdf"),  # (ۋ, ﯞ, , , ﯟ),
    ("\u06cc", "\ufbfc", "\ufbfe", "\ufbff", "\ufbfd"),  # (ی, ﯼ, ﯾ, ﯿ, ﯽ),
    ("\u06d0", "\ufbe4", "\ufbe6", "\ufbe7", "\ufbe5"),  # (ې, ﯤ, ﯦ, ﯧ, ﯥ),
    ("\u06d2", "\ufbae", "", "", "\ufbaf"),  # (ے, ﮮ, , , ﮯ),
    ("\u06d3", "\ufbb0", "", "", "\ufbb1"),  # (ۓ, ﮰ, , , ﮱ),
    ("\ufefb", "\ufefb", "", "", "\ufefc"),  # (ﻻ, ﻻ, , , ﻼ),
    ("\ufef7", "\ufef7", "", "", "\ufef8"),  # (ﻷ, ﻷ, , , ﻸ),
    ("\ufef5", "\ufef5", "", "", "\ufef6"),  # (ﻵ, ﻵ, , , ﻶ),
    ("\ufef9", "\ufef9", "", "", "\ufefa"),  # (ﻹ, ﻹ, , , ﻺ),
)

unshaped_to_isolated = {x[UNSHAPED]: x[ISOLATED] for x in shapes_table}

mandatory_liga_table = {
    ("\ufedf", "\ufe82"): "\ufef5",  # ['ﻟ', 'ﺂ', 'ﻵ']
    ("\ufedf", "\ufe84"): "\ufef7",  # ['ﻟ', 'ﺄ', 'ﻷ']
    ("\ufedf", "\ufe88"): "\ufef9",  # ['ﻟ', 'ﺈ', 'ﻹ']
    ("\ufedf", "\ufe8e"): "\ufefb",  # ['ﻟ', 'ﺎ', 'ﻻ']
    ("\ufee0", "\ufe82"): "\ufef6",  # ['ﻠ', 'ﺂ', 'ﻶ']
    ("\ufee0", "\ufe84"): "\ufef8",  # ['ﻠ', 'ﺄ', 'ﻸ']
    ("\ufee0", "\ufe88"): "\ufefa",  # ['ﻠ', 'ﺈ', 'ﻺ']
    ("\ufee0", "\ufe8e"): "\ufefc",  # ['ﻠ', 'ﺎ', 'ﻼ']
}

# lam = '\u0644'
lamalif_to_alif = {
    "\ufef5": "\u0622",  # [ 'آ', 'ﻵ']
    "\ufef7": "\u0623",  # ['ﺃ', 'ﻷ']
    "\ufef9": "\u0625",  # [ 'ﺇ', 'ﻹ']
    "\ufefb": "\u0627",  # ['ﺍ', 'ﻻ']
}

HARAKAT_RE = re.compile(
    "["
    "\u0610-\u061a"
    "\u064b-\u065f"
    "\u0670"
    "\u06d6-\u06dc"
    "\u06df-\u06e8"
    "\u06ea-\u06ed"
    "\u08d4-\u08e1"
    "\u08d4-\u08ed"
    "\u08e3-\u08ff"
    "]",
    re.UNICODE | re.X,
)

ARABIC_RE = re.compile(
    "["
    "\u0600-\u060a"
    "\u060c-\u06ff"
    "\u0750-\u077f"
    "\u08a0-\u08ff"
    "\u206c-\u206d"
    "\ufb50-\ufd3d"
    "\ufd50-\ufdfb"
    "\ufe70-\ufefc"
    "]",
    re.UNICODE | re.X,
)

NUMBERS_RE = re.compile(
    "["
    "\u0660-\u0669"  # indic numbers
    "\u0030-\u0039"  # arabic numbers
    "]",
    re.UNICODE | re.X,
)

NEUTRAL_RE = re.compile(
    "[" "\u0000-\u0040" "\u005b-\u0060" "\u007b-\u007f" "]", re.UNICODE | re.X
)


def remove_harakat(text):
    result = [c for c in text if not HARAKAT_RE.match(c)]
    # print(HARAKAT_RE.match(c))
    return "".join(result)


def do_ligation(text):
    result = []

    for i, c in enumerate(text):
        shape = mandatory_liga_table.get((c, text[i - 1]), None)
        if shape:
            result.pop()
            result.append(shape)
        else:
            result.append(c)

    return "".join(result)


def do_shaping(text):
    def get_shapes(c):
        # get all different letter shapes
        if c is None:
            return {}
        key = c
        match = [v for v in shapes_table if key in v]
        if match:
            match = match[UNSHAPED]
            return {
                ISOLATED: match[ISOLATED],
                INITIAL: match[INITIAL],
                MEDIAL: match[MEDIAL],
                FINAL: match[FINAL],
            }
        else:
            return {}

    def get_shape(c, right_char, left_char):
        """get a proper letter shape
        Args:
            c: current letter
            right_char: letter before
            left_char: letter after
        """
        c_shapes = get_shapes(c)

        if c_shapes and c_shapes.get(FINAL):
            # letter is arabic
            right_char_shapes = get_shapes(right_char)
            left_char_shapes = get_shapes(left_char)

            position = MEDIAL if right_char_shapes.get(MEDIAL) else INITIAL
            alternative = {MEDIAL: FINAL, INITIAL: ISOLATED}
            if not isarabic(left_char):
                position = alternative[position]
            elif not left_char_shapes.get(FINAL):
                position = ISOLATED

            c = c_shapes.get(position) or c_shapes.get(alternative[position])

        return c

    t = []
    for i in range(len(text) - 1, -1, -1):
        c = text[i]
        right_char = text[i + 1] if i < len(text) - 1 else None
        left_char = text[i - 1] if i > 0 else None
        t.insert(0, get_shape(c, right_char, left_char))
    return "".join(t)


def workaround_for_windows_auto_bidi(text):
    """workaround to disable windows auto-bidi
    we should pass only ISOLATED form of arabic letters
    since unshaped letters trigger windows bidi engine

    """
    # todo: should find away to disable windows bidi completely

    # convert all unshaped letters to isolated to bypass windows auto-bidi
    text = "".join([unshaped_to_isolated.get(c, c) for c in text])

    # remove arabic TATWEEL letter '\u0640', it has no isolated form
    text = text.replace("\u0640", "")

    return text


def reshaper(text):
    text = do_shaping(text)
    text = do_ligation(text)
    text = remove_harakat(text)

    if operating_system == "Windows":
        text = workaround_for_windows_auto_bidi(text)

    return text


def renderBiDiText(text):
    if operating_system not in ["Windows", "Darwin"]:
        text = get_display(text)
        text = reshaper(text)
        return text
    return text


def derender_bidi_text(text):
    # convert visual text to logical

    # get unshaped characters
    unshaped_text = []
    for c in text:
        match = [item[0] for item in shapes_table if c in item]
        if match:
            c = match[0]

        # lam-alif decomposition
        if c in lamalif_to_alif:
            alif = lamalif_to_alif[c]
            lam = "\u0644"
            unshaped_text.append(alif)
            c = lam

        unshaped_text.append(c)

    # reverse text order to its original state
    text = get_display("".join(unshaped_text))

    return text


def split_path(path):
    """
    split path into individual parts

    Args:
        path(str): string representation of a path, e.g: '/home/Desktop'

    Return:
        list of splitted path

    credit: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
    """

    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def render_bidi_path(path):
    """
    render bidi words in path string

    Args:
        path(str): string representation of a path, e.g: '/home/Desktop'

    Return:
        (str) rendered path

    """
    parts = split_path(path)
    parts = [renderBiDiText(x) for x in parts]
    return os.path.join(*parts)


def derender_bidi_path(path):
    """
    reverse of render_bidi_path
    """
    parts = split_path(path)
    parts = [derender_bidi_text(x) for x in parts]
    return os.path.join(*parts)


def render_text(text, ispath=False):
    """
    render bidi text

    Args:
        text(str): input text that contains a bidi words e.g: English words mixed with Arabic words
        ispath(bool): whether the text argument is path or not, e.g: '/usr/bin/etc'

    Returns:
        (str): rendered text
    """
    if ispath:
        return render_bidi_path(text)
    else:
        return renderBiDiText(text)


def derender_text(text, ispath=False):
    if ispath:
        return derender_bidi_path(text)
    else:
        return derender_bidi_text(text)


def isarabic(c):
    if isinstance(c, str):
        match = ARABIC_RE.match(c)
        return match
    return False


def is_neutral(c):
    if isinstance(c, str):
        match = NEUTRAL_RE.match(c)
        return match
    return False


def handle_entry(event, widget):
    try:
        if widget.focus_get() != widget:  # sometimes it raise an exception
            return
    except Exception:
        return

    def move_cursor_to_left():
        # control direction
        current_index = widget.index(tk.INSERT)
        new_index = current_index - 1 if current_index >= 1 else 0
        widget.icursor(new_index)

    c = event.char
    index = widget.index("insert")

    if not (
        c or event.keysym in ("BackSpace", "Delete") or isarabic(c) or is_neutral(c)
    ):
        return

    if NUMBERS_RE.match(event.char):
        return

    if isarabic(c):
        widget.RTL = True
        move_cursor_to_left()
    # handle backspace
    elif event.keysym in ("BackSpace", "Delete"):
        try:
            widget.delete("sel.first", "sel.last")
        except Exception:
            if (
                widget.RTL
                and event.keysym == "BackSpace"
                or not widget.RTL
                and event.keysym == "Delete"
            ):
                widget.delete(index)
            elif index > 0:
                widget.delete(index - 1)

    elif is_neutral(c) and widget.RTL:
        move_cursor_to_left()
    else:
        widget.RTL = False

    if widget.last_text == widget._get():
        return

    text = widget._get()
    index = widget.index("insert")
    widget.delete(0, "end")

    text = reshaper(text)

    widget.insert(0, text)
    widget.icursor(index)

    widget.last_text = widget._get()


def add_bidi_support_for_entry(widget):
    """add arabic support for an entry widget"""

    def handledeletion(event):
        handle_entry(event, widget)
        return "break"

    widget.RTL = False
    widget.last_text = ""
    widget.bind("<BackSpace>", handledeletion)
    widget.bind("<Delete>", handledeletion)
    widget._get = widget.get
    widget.get = lambda: derender_bidi_text(widget._get())

    def set_text(text):
        widget.delete(0, "end")
        widget.insert(0, renderBiDiText(text))

    widget.set = set_text

    widget.bind_all("<KeyPress>", lambda event: handle_entry(event, widget), add="+")


def add_bidi_support_for_label(widget):
    """add arabic support for an entry widget"""

    def get_text():
        return derender_bidi_text(widget["text"])

    def set_text(text):
        widget["text"] = renderBiDiText(text)
        print(renderBiDiText(text))

    set_text(widget["text"])
    widget.get = get_text
    widget.set = set_text


def add_bidi_support_for_button(widget):
    """Add Arabic support for a button widget."""

    def get_text():
        print(derender_bidi_text(widget.cget("text")))
        return derender_bidi_text(widget.cget("text"))

    def set_text(text):
        widget.configure(text=renderBiDiText(text))

    set_text(widget.cget("text"))
    widget.get = get_text
    widget.set = set_text


def add_bidi_support(
    widget, render_copy_paste=True, copy_paste_menu=False, ispath=False
):
    """add bidi support for tkinter widget"""
    if widget.winfo_class() == "Label":
        add_bidi_support_for_label(widget)
    elif widget.winfo_class() == "Entry":
        add_bidi_support_for_entry(widget)
        if render_copy_paste:
            override_copy_paste(widget, ispath=ispath, copy_paste_menu=copy_paste_menu)
    elif widget.winfo_class() == "Button":
        add_bidi_support_for_button(widget)


def override_copy_paste(
    widget,
    copyrender=derender_text,
    pasterender=render_text,
    ispath=False,
    copy_paste_menu=False,
):
    def copy(value):
        """copy clipboard value

        Args:
            value (str): value to be copied to clipboard
        """
        try:
            widget.clipboard_clear()
            widget.clipboard_append(str(value))
        except Exception:
            pass

    def paste():
        """get clipboard value"""
        try:
            value = widget.clipboard_get()
        except Exception:
            value = ""

        return value

    def copy_callback(*args):
        try:
            selected_text = widget.selection_get()
            derendered_text = copyrender(selected_text, ispath=ispath)
            copy(str(derendered_text))

        except Exception:
            pass

        return "break"

    def paste_callback(*args):
        try:
            widget.delete("sel.first", "sel.last")
        except Exception:
            pass

        try:
            text = paste()
            rendered_text = pasterender(text, ispath=ispath)
            widget.insert(tk.INSERT, rendered_text)
        except Exception:
            pass

        return "break"

    # bind
    widget.bind("<<Copy>>", copy_callback)
    widget.bind("<<Paste>>", paste_callback)

    # reference copy paste
    widget.copy_callback = copy_callback
    widget.paste_callback = paste_callback

    # right click menu
    def rcm_handler(option):
        if option.lower() == "copy":
            copy_callback()
        else:
            paste_callback()

    if copy_paste_menu:
        widget.rcm = RightClickMenu(widget, ["copy", "paste"], callback=rcm_handler)


if __name__ == "__main__":
    root = tk.Tk()
    txt = "السلام عليكم"

    # text display incorrectly on linux
    dummyvar = tk.StringVar()
    dummyvar.set(txt)
    tk.Label(root, textvariable=dummyvar, font="any 20").pack()

    # uncomment below to set a rendered text to first label
    dummyvar.set(renderBiDiText(txt))

    entry = tk.Entry(root, font="any 20", justify="right")
    entry.pack()

    lbl = tk.Label(root, font="any 20")
    lbl.pack()

    # adding bidi support for widgets
    add_bidi_support(lbl)
    add_bidi_support(entry)

    # we can use set() and get() methods to set and get text on a widget
    entry.set(txt)
    lbl.set("هذا كتاب adventure شيق")

    root.mainloop()
