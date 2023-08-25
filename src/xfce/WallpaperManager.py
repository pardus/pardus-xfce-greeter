#!/usr/bin/env python3

import os
import subprocess

wallpaper_dir = "/usr/share/backgrounds/"


def getWallpaperList():
    wallpapers = []
    # Add wallpapers to list
    for root, dirs, files in os.walk(wallpaper_dir):
        dirs.clear()
        for file_name in files:
            path = os.path.join(root, file_name)
            wallpapers.append(f"{path}")

    return wallpapers


def setWallpaper(wallpaper):
    subprocess.call([
        "/bin/sh", "-c",
        f"xfconf-query -c xfce4-desktop -l | grep last-image | while read path; do xfconf-query -c xfce4-desktop -p $path -s {wallpaper}; done"
    ])


def getResolution():
    output = subprocess.check_output("xrandr | grep '*'", shell=True).decode("utf-8")
    return output.strip().split(" ")[0]
