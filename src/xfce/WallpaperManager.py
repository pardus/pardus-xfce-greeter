import os, subprocess


folders = ["/usr/share/backgrounds/"]
desktopBaseFolder = "/usr/share/desktop-base/active-theme/wallpaper/contents/images/"
prefixs = ["jpg","png","bmp","jpeg","svg"]

def getWallpaperList():
    currentResolution = getResolution()
    currentResolutionTuple = (int(currentResolution.split("x")[0]), int(currentResolution.split("x")[1]))
    nearestResolution = (1, 1)
    nearestResolutionFile = ""
    pictures = []

    # Get all resolutions from desktop-base and select Current system resolution if exists
    desktopBaseFiles = os.walk(desktopBaseFolder)
    for (_, _, files) in desktopBaseFiles:
        for file in files:
            fileResolution = (int(file[:-4].split("x")[0]), int(file[:-4].split("x")[1]))
            #print(f"Current: {currentResolutionTuple}, File: {fileResolution}, Fark:{abs(currentResolutionTuple[0] - fileResolution[0])}, {abs(currentResolutionTuple[1] - fileResolution[1])}")
            if abs(currentResolutionTuple[0] - fileResolution[0]) <= abs(currentResolutionTuple[0] - nearestResolution[0]):
                if abs(currentResolutionTuple[1] - fileResolution[1]) <= abs(currentResolutionTuple[1] - nearestResolution[1]):
                    #print(f"en uygun bulundu: {fileResolution}, Fark:{abs(currentResolutionTuple[0] - nearestResolution[0])}, {abs(currentResolutionTuple[1] - nearestResolution[1])}")
                    nearestResolution = fileResolution
                    nearestResolutionFile = file
    
    # Add desktop-base wallpaper to list
    pictures.append(f"{desktopBaseFolder}{nearestResolutionFile}")

    # Add other wallpapers to list
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
        "/bin/sh", "-c",
        f"xfconf-query -c xfce4-desktop -l | grep last-image | while read path; do xfconf-query -c xfce4-desktop -p $path -s {wallpaper}; done"
    ])


def getResolution():
    output = subprocess.check_output("xrandr | grep '*'", shell=True).decode("utf-8")
    return output.strip().split(" ")[0]