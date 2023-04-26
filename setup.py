#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "pardus-welcome.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/pardus-welcome.mo"]))
    return mo


changelog = "debian/changelog"
version = "0.1.0"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
 ("/usr/share/applications/", ["tr.org.pardus.welcome.desktop"]),
 ("/usr/share/pardus/pardus-welcome/assets",
  ["assets/pardus-welcome.svg", "assets/pardus-logo.svg", "assets/theme-light.png",
   "assets/theme-dark.png", "assets/progress-dot-on.svg", "assets/progress-dot-off.svg",
   "assets/whisker.png", "assets/discord.svg", "assets/github.svg"]),
 ("/usr/share/pardus/pardus-welcome/src", ["src/Main.py", "src/MainWindow.py", "src/utils.py"]),
 ("/usr/share/pardus/pardus-welcome/src/xfce",
  ["src/xfce/WallpaperManager.py", "src/xfce/ThemeManager.py", "src/xfce/ScaleManager.py",
   "src/xfce/KeyboardManager.py", "src/xfce/WhiskerManager.py", "src/xfce/PanelManager.py"]),
 ("/usr/share/pardus/pardus-welcome/src/gnome",
  ["src/gnome/WallpaperManager.py", "src/gnome/ThemeManager.py", "src/gnome/ScaleManager.py"]),
 ("/usr/share/pardus/pardus-welcome/ui", ["ui/MainWindow.glade"]),
 ("/usr/bin/", ["pardus-welcome"]),
 ("/etc/skel/.config/autostart", ["tr.org.pardus.welcome.desktop"]),
 ("/usr/share/icons/hicolor/scalable/apps/", ["assets/pardus-welcome.svg"])
] + create_mo_files()

setup(
    name="Pardus Welcome",
    version=version,
    packages=find_packages(),
    scripts=["pardus-welcome"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Emin Fedar",
    author_email="emin.fedar@pardus.org.tr",
    description="Pardus Greeter at first login.",
    license="GPLv3",
    keywords="start setup settings theme wallpaper",
    url="https://github.com/pardus/pardus-welcome",
)
