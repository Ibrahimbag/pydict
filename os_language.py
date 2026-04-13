import os
import locale
import ctypes


def get_os_language():
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        language = locale.windows_locale[kernel32.GetUserDefaultUILanguage()]
        return language.split("_")[0]  # Return the language code without region
    elif os.name == "posix":
        language = os.getenv("LANG").split("_")[0]
        return language
