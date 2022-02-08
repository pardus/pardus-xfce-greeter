#!/usr/bin/env python3
from setuptools import setup, find_packages, os
from shutil import copyfile

changelog = 'debian/changelog'
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = ""
    f = open('src/__version__', 'w')
    f.write(version)
    f.close()

data_files = [
    ("/usr/share/applications/", ["tr.org.pardus.welcome.desktop"]),
    ("/usr/share/locale/tr/LC_MESSAGES/", ["translations/tr/LC_MESSAGES/pardus-welcome.mo"]),
    ("/usr/share/pardus/pardus-welcome/assets", ["assets/pardus-welcome.svg", "assets/pardus-logo.svg", "assets/theme-light.png", "assets/theme-dark.png", "assets/progress-dot-on.svg", "assets/progress-dot-off.svg", "assets/whisker.png"]),
    ("/usr/share/pardus/pardus-welcome/src", ["src/main.py", "src/MainWindow.py", "src/utils.py"]),
    ("/usr/share/pardus/pardus-welcome/src/xfce", ["src/xfce/WallpaperManager.py", "src/xfce/ThemeManager.py", "src/xfce/ScaleManager.py", "src/xfce/KeyboardManager.py", "src/xfce/WhiskerManager.py", "src/xfce/PanelManager.py"]),
    ("/usr/share/pardus/pardus-welcome/src/gnome", ["src/gnome/WallpaperManager.py", "src/gnome/ThemeManager.py", "src/gnome/ScaleManager.py"]),
    ("/usr/share/pardus/pardus-welcome/ui", ["ui/MainWindow.glade"]),
    ("/usr/bin/", ["pardus-welcome"]),
    ("/etc/skel/.config/autostart", ["tr.org.pardus.welcome.desktop"]),
    ("/usr/share/icons/hicolor/scalable/apps/", ["assets/pardus-welcome.svg"])
]

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
    url="https://www.pardus.org.tr",
)
