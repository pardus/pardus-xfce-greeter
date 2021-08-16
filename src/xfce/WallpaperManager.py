import os, subprocess


folders = ["/usr/share/backgrounds/"]
desktopBaseFolder = "/usr/share/desktop-base/active-theme/wallpaper/contents/images/"
prefixs = ["jpg","png","bmp","jpeg","svg"]

def getWallpaperList():
    currentResolution = getResolution()
    desktopBaseResolutions = []
    pictures = []

    # Get all resolutions from desktop-base and select Current system resolution if exists
    desktopBaseFiles = os.walk(desktopBaseFolder)
    for (_, _, files) in desktopBaseFiles:
        for file in files:
            desktopBaseResolutions.append(f"{file}")
    
    # Add other wallpapers to list
    for path in folders:
        paths = os.walk( path )
        for (dirpath, _, files) in paths:
            for file in files:
                for prefix in prefixs:
                    if file[-3:] == prefix:
                        pictures.append(f"{dirpath}/{file}")
                        break
    
    # Add desktop-base wallpaper to list
    if f"{currentResolution}.svg" in desktopBaseResolutions:
        pictures.append(f"{desktopBaseFolder}{currentResolution}.svg")
    else:
        pictures = pictures + desktopBaseResolutions
    
    return pictures

def setWallpaper(wallpaper):
    subprocess.call([
        "gsettings",
        "set",
        "org.gnome.desktop.background",
        "picture-uri",
        f"file://{wallpaper}"
    ])


def getResolution():
    output = subprocess.check_output("xrandr | grep '*'", shell=True).decode("utf-8")
    return output.strip().split(" ")[0]