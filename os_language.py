import os
import locale
import ctypes


def get_os_language():
    if os.name == "nt":
        windll = ctypes.windll.kernel32
        windll.GetUserDefaultUILanguage()
        language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
        return language.split("_")[0]  # Return the language code without region
    elif os.name == "posix":
        language = os.getenv('LANG').split("_")[0]
        language = "tr"
        return language
