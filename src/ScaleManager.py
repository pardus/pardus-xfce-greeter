import subprocess

defaultDPI = 96

def setScale(percent):
    newDPI = 96 * percent / 100
    subprocess.call([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Xft/DPI",
        "-s", str(int(newDPI)),
        "--type", "int",
        "--create"
    ])
def setPanelSize(px):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", "/panels/panel-1/size",
        "-s", str(px),
        "--type", "int",
        "--create"
    ])

def setPanelIconSize(px):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", "/panels/panel-1/icon-size",
        "-s", str(px),
        "--type", "int",
        "--create"
    ])

def setDesktopIconSize(px):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-desktop",
        "-p", "/desktop-icons/icon-size",
        "-s", str(px),
        "--type", "int",
        "--create"
    ])

def getScale():
    dpi = int(subprocess.check_output([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Xft/DPI",
    ]).decode("utf-8").rstrip())

    return int(dpi * 100 / 96)
def getPanelSize():
    return int(subprocess.check_output([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", "/panels/panel-1/size"
    ]).decode("utf-8").rstrip())

def getPanelIconSize():
    return int(subprocess.check_output([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", "/panels/panel-1/icon-size"
    ]).decode("utf-8").rstrip())

def getDesktopIconSize():
    return int(subprocess.check_output([
        "xfconf-query",
        "-c", "xfce4-desktop",
        "-p", "/desktop-icons/icon-size"
    ]).decode("utf-8").rstrip())
