import os
import locale
import ctypes


def get_os_language():
    if os.name == "nt":
        windll = ctypes.windll.kernel32
        windll.GetUserDefaultUILanguage()
        language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
        return language.split("_")[0]  # Return the language code without region
    # TODO: Add support for Linux and MacOS
    elif os.name == "posix":
        ...
        # os.getenv('LANG')
