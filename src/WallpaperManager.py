import os, subprocess

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

folders = ["/usr/share/backgrounds/"]
prefixs = ["jpg","png","bmp","jpeg"]

def getWallpaperList():
    pictures = []
    for path in folders:
        paths = os.walk( path )
        for (dirpath, _, files) in paths:
            for file in files:
                for prefix in prefixs:
                    if file[-3:] == prefix:
                        pictures.append(f"{dirpath}/{file}")
                        break
    
    return pictures

def setWallpaper(wallpaper):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-desktop",
        "-p", "/backdrop/screen0/monitor0/workspace0/last-image",
        "-s", wallpaper,
        "--type", "string",
        "--create"
    ])       
