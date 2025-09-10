import os
import subprocess

import gi

gi.require_version("Xfconf", "0")
from gi.repository import Xfconf

wallpaper_dir = "/usr/share/backgrounds/"


def get_wallpapers():
    wallpapers = []
    # Add wallpapers to list
    for root, dirs, files in os.walk(wallpaper_dir):
        dirs.clear()
        for file_name in files:
            path = os.path.join(root, file_name)
            wallpapers.append(f"{path}")

    return wallpapers


def set_wallpaper(wallpaper):
    desktop = Xfconf.Channel.new("xfce4-desktop")
    properties = desktop.get_properties("/backdrop")

    for p in properties:
        if "screen" in p and ("last-image" in p or "last-single-image" in p):
            desktop.set_string(p, wallpaper)


def get_resolution():
    output = subprocess.check_output("xrandr | grep '*'", shell=True).decode("utf-8")
    return output.strip().split(" ")[0]
