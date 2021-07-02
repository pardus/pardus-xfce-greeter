import os

# PATHS
HOME_PATH = os.environ.get('HOME', None)
WHISKER_FILE_PATH = f"{HOME_PATH}/.config/xfce4/panel/whiskermenu-2.rc"

# READ FILE
configFileData = ""
with open(WHISKER_FILE_PATH, 'r') as file:
    configFileData = file.read()

def set(key, value):
    global configFileData

    lines = configFileData.splitlines()
    for i in range(len(lines)):
        if key in lines[i]:
            print(f"{key} found: {lines[i]}")
            lines[i] = f"{key}={value}"
    
    configFileData = "\n".join(lines)

def saveFile():
    global configFileData
    
    with open(WHISKER_FILE_PATH, 'w') as file:
        file.write(configFileData)

#print(configFileData) before
#set("launcher-show-name", "true")
#print(configFileData) after