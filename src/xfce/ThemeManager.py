import os, subprocess, pwd

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

USER = pwd.getpwuid(os.getuid()).pw_name

themePath = ["/usr/share/themes/", f"/home/{USER}/.themes/"]

def getThemeList():
    themes = []
    windowThemes = []

    for path in themePath:
        try:
            files = os.scandir( path )
            for file in files:
                if file.is_dir():
                    themes.append(file.name)
                    
                    if os.path.isdir(f"{path}/{file.name}/xfwm4"):
                        windowThemes.append(file.name)
        except FileNotFoundError as error:
            pass
    
    themes.sort()
    windowThemes.sort()
    return [themes, windowThemes]

def setTheme(theme):
    subprocess.call([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Net/ThemeName",
        "-s", theme,
        "--type", "string",
        "--create"
    ])

def setWindowTheme(theme):
    subprocess.call([
        "xfconf-query",
        "-c", "xfwm4",
        "-p", "/general/theme",
        "-s", theme,
        "--type", "string",
        "--create"
    ])

def setIconTheme(theme):
    subprocess.call([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Net/IconThemeName",
        "-s", theme,
        "--type", "string",
        "--create"
    ])

def getTheme():
    return subprocess.check_output([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Net/ThemeName"
    ]).decode("utf-8").rstrip()

def getWindowTheme():
    return subprocess.check_output([
        "xfconf-query",
        "-c", "xfwm4",
        "-p", "/general/theme"
    ]).decode("utf-8").rstrip()

def getIconTheme():
    return subprocess.check_output([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Net/IconThemeName",
    ]).decode("utf-8").rstrip()
