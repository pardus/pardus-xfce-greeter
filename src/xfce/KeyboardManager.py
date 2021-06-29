import subprocess, re

keyboardLayouts = ["tr","tr","us"]
keyboardVariants = ["f", "", ""]
keyboardStatus = [False, False, False]

keyboardPlugin = ""

def setKeyboardState():
    layoutString = ""
    variantString = ""
    for i in range(len(keyboardLayouts)):
        if keyboardStatus[i]:
            layoutString += keyboardLayouts[i] + ","
            variantString += keyboardVariants[i] + ","
    
    layoutString = layoutString[:-1]
    variantString = variantString[:-1]
    
    subprocess.call([
        "xfconf-query",
        "-c", "keyboard-layout",
        "-p", "/Default/XkbLayout",
        "-s", layoutString,
        "--type", "string",
        "--create"
    ])
    subprocess.call([
        "xfconf-query",
        "-c", "keyboard-layout",
        "-p", "/Default/XkbVariant",
        "-s", variantString,
        "--type", "string",
        "--create"
    ])

def setTurkishF(state):
    keyboardStatus[0] = state
    setKeyboardState()

def setTurkishQ(state):
    keyboardStatus[1] = state
    setKeyboardState()

def setEnglish(state):
    keyboardStatus[2] = state
    setKeyboardState()

def getKeyboardState():
    try:
        layouts = subprocess.check_output([
            "xfconf-query",
            "-c", "keyboard-layout",
            "-p", "/Default/XkbLayout"
        ]).decode("utf-8").rstrip().split(",")
        variants = subprocess.check_output([
            "xfconf-query",
            "-c", "keyboard-layout",
            "-p", "/Default/XkbVariant"
        ]).decode("utf-8").rstrip().split(",")

        global keyboardLayouts
        global keyboardVariants
        global keyboardStatus

        for i in range(len(layouts)):
            for j in range(len(keyboardLayouts)):
                if layouts[i] == keyboardLayouts[j] and variants[i] == keyboardVariants[j]:
                    keyboardStatus[j] = True
        
        return keyboardStatus
    except subprocess.CalledProcessError:
        setKeyboardState()
        return getKeyboardState()



# PLUGIN:
def createKeyboardPlugin():
    # Add keyboard
    subprocess.call([
        "xfce4-panel",
        "--add=xkb"
    ])

    getKeyboardPlugin()
    
    # Display Language Name (not country)
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", f"/plugins/{keyboardPlugin}/display-name",
        "-s", "1",
        "--type", "int",
        "--create"
    ])

    # Display text (not flag)
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", f"/plugins/{keyboardPlugin}/display-type",
        "-s", "2",
        "--type", "int",
        "--create"
    ])

    # Enable globally (not program-wide)
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", f"/plugins/{keyboardPlugin}/group-policy",
        "-s", "0",
        "--type", "int",
        "--create"
    ])

def removeKeyboardPlugin():
    # Remove plugin
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", f"/plugins/{keyboardPlugin}",
        "-r", "-R"
    ])
    # Refresh panel
    subprocess.call([
        "xfce4-panel",
        "-r"
    ])


def getKeyboardPlugin():
    global keyboardPlugin

    pluginList = subprocess.check_output([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-l", "-v"
    ]).decode("utf-8").splitlines()

    for line in pluginList:
        if len(re.findall("xkb", line)) > 0:
            keyboardPlugin = line.split("/")[2].split(" ")[0]
            return keyboardPlugin
    
    return ""

def disableSystemsKeyboard():
    subprocess.call([
        "xfconf-query",
        "-c", "keyboard-layout",
        "-p", f"/Default/XkbDisplay",
        "-s", "false",
        "--type", "bool",
        "--create"
    ])

disableSystemsKeyboard()