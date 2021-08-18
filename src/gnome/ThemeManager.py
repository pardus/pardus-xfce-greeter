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
        except FileNotFoundError as error:
            pass
    
    themes.sort()
    return [themes, windowThemes]

def setTheme(theme):
    subprocess.call([
        "gsettings",
        "set",
        "org.gnome.desktop.interface",
        "gtk-theme",
        f"'{theme}'"
    ])

def setIconTheme(theme):
    subprocess.call([
        "gsettings",
        "set",
        "org.gnome.desktop.interface",
        "icon-theme",
        f"'{theme}'"
    ])

def getTheme():
    return subprocess.check_output([
        "gsettings",
        "get",
        "org.gnome.desktop.interface",
        "gtk-theme"
    ]).decode("utf-8").rstrip()

def getIconTheme(theme):
    return subprocess.check_output([
        "gsettings",
        "get",
        "org.gnome.desktop.interface",
        "icon-theme"
    ]).decode("utf-8").rstrip()