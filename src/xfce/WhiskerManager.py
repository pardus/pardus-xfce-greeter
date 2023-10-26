#!/usr/bin/env python3

import os

# PATHS
HOME_PATH = os.environ.get('HOME', None)
WHISKER_FILE_PATH = f"{HOME_PATH}/.config/xfce4/panel/whiskermenu-2.rc"

whisker_file_found = False

if os.path.exists(WHISKER_FILE_PATH):
    whisker_file_found = True
    # READ FILE
    configFileData = ""
    with open(WHISKER_FILE_PATH, 'r') as file:
        configFileData = file.read()
else:
    print("{} not exists".format(WHISKER_FILE_PATH))

def set(key, value):
    if not whisker_file_found:
        return
    global configFileData

    lines = configFileData.splitlines()
    for i in range(len(lines)):
        if key == lines[i].split("=")[0]:
            print(f"{key} found: {lines[i]}")
            lines[i] = f"{key}={value}"

    configFileData = "\n".join(lines)


def saveFile():
    if not whisker_file_found:
        return
    global configFileData

    with open(WHISKER_FILE_PATH, 'w') as file:
        file.write(configFileData)

# print(configFileData) # before
# set("launcher-show-name", "true")
# print(configFileData) # after
