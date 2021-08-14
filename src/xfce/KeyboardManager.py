import subprocess, re

keyboardLayouts = ["tr","tr","us"]
keyboardVariants = ["", "f", ""]
keyboardStatus = [False, False, False]

keyboardPlugin = ""

def initializeSettings():
    # Add Super + Space combination to change layouts
    subprocess.call([
        "xfconf-query",
        "-c", "keyboard-layout",
        "-p", "/Default/XkbOptions/Group",
        "-s", "grp:win_space_toggle",
        "--type", "string",
        "--create"
    ])

    # Get system settings if disabled
    useSystemKeyboard = subprocess.check_output([
        "xfconf-query",
        "-c", "keyboard-layout",
        "-p", "/Default/XkbDisable",
    ]).decode("utf-8").rstrip() == "true"

    if useSystemKeyboard:
        getSystemKeyboardState()
        setKeyboardState()

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
    subprocess.call([
        "xfconf-query",
        "-c", "keyboard-layout",
        "-p", "/Default/XkbDisable",
        "-s", "false",
        "--type", "bool",
        "--create"
    ])

# Add Keyboard Layouts:
def setTurkishQ(state):
    keyboardStatus[0] = state
    setKeyboardState()

def setTurkishF(state):
    keyboardStatus[1] = state
    setKeyboardState()

def setEnglish(state):
    keyboardStatus[2] = state
    setKeyboardState()

# Get System's Keyboard
def getSystemKeyboardState():
    layoutProcess = subprocess.run("cat /etc/default/keyboard | grep XKBLAYOUT | tr -d '\"'", shell=True, capture_output=True)
    variantProcess = subprocess.run("cat /etc/default/keyboard | grep XKBVARIANT | tr -d '\"'", shell=True, capture_output=True)
    
    layout = layoutProcess.stdout.decode("utf-8").rstrip().split("=")[1]
    variant = variantProcess.stdout.decode("utf-8").rstrip().split("=")[1]

    global keyboardLayouts
    global keyboardVariants
    global keyboardStatus

    for j in range(len(keyboardLayouts)):
        if layout == keyboardLayouts[j] and variant == keyboardVariants[j]:
            keyboardStatus[j] = True
        
    return keyboardStatus

# Get Current Keyboard State
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
        getSystemKeyboardState() # First get systemwide keyboard
        setKeyboardState() # Save it
        return keyboardStatus



# PLUGIN:
def createKeyboardPlugin():
    # Add keyboard
    subprocess.call([
        "xfce4-panel",
        "--add=xkb"
    ])

    getKeyboardPlugin()
    changeKeyboardPluginPlacement()
    
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

def changeKeyboardPluginPlacement():
    pluginList = subprocess.check_output([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", "/panels/panel-1/plugin-ids"
    ]).decode("utf-8").splitlines()[2:]
    
    if keyboardPlugin.split("-")[1] == pluginList[-2]:
        return
    
    pluginList[-1], pluginList[-2] = pluginList[-2], pluginList[-1]
    

    setArrayCommand = []
    for i in range(len(pluginList)):
        setArrayCommand.append("-t")
        setArrayCommand.append("int")

    for i in range(len(pluginList)):
        setArrayCommand.append("-s")
        setArrayCommand.append(pluginList[i])
    

    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-panel",
        "-p", "/panels/panel-1/plugin-ids",
        "-n"
    ] + setArrayCommand)

    subprocess.call([
        "xfce4-panel",
        "-r"
    ])