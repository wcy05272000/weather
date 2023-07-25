import winreg


def is_dark_mode():
    mydir = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, mydir)
    value, type_ = winreg.QueryValueEx(key, "AppsUseLightTheme")
    winreg.CloseKey(key)

    if value == 0:
        text = 'dark'
        return text
    elif value == 1:
        text = 'light'
        return text


