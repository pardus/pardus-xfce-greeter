#!/usr/bin/env python3
from setuptools import setup, find_packages, os

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
    ("/usr/share/pardus/pardus-welcome/", ["icon.svg", "pardus-logo.svg", "theme-light.png", "theme-dark.png"]),
    ("/usr/share/pardus/pardus-welcome/src",
     ["src/main.py", "src/MainWindow.py", "src/utils.py",
        "src/xfce/WallpaperManager.py", "src/xfce/ThemeManager.py", "src/xfce/ScaleManager.py",
        "src/gnome/WallpaperManager.py", "src/gnome/ThemeManager.py", "src/gnome/ScaleManager.py"]),
    ("/usr/share/pardus/pardus-image-writer/ui", ["ui/MainWindow.glade"]),
    ("/usr/bin/", ["pardus-welcome"])
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
