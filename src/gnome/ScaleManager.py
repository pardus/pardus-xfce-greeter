import subprocess

defaultDPI = 96

def setScale(scaling_factor):
    subprocess.call([
        "gsettings",
        "set",
        "org.gnome.desktop.interface",
        "text-scaling-factor",
        f"{scaling_factor}"
    ])

def getScale():
    try:
        scaling_factor = float(subprocess.check_output([
            "gsettings",
            "get",
            "org.gnome.desktop.interface",
            "text-scaling-factor"
        ]).decode("utf-8").rstrip())
    except:
        return 1.0

    return scaling_factor
