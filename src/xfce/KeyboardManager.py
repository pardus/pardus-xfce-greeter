import subprocess
import gi

gi.require_version("Xfconf", "0")
from gi.repository import Xfconf

keyboard_layout = Xfconf.Channel.new("keyboard-layout")
xfce4_panel = Xfconf.Channel.new("xfce4-panel")


def init():
    # Add Super + Space combination to change layouts
    keyboard_layout.set_string("/Default/XkbOptions/Group", "grp:win_space_toggle")

    # Get system settings if disabled
    use_system_keyboard = keyboard_layout.get_bool("/Default/XkbDisable", False)

    if use_system_keyboard:
        get_system_keyboards()


def get_layouts():
    layouts = keyboard_layout.get_string("/Default/XkbLayout", "")  # "tr,tr,us"
    variants = keyboard_layout.get_string("/Default/XkbVariant", "")  # ",f,"

    # "tr,tr,us"
    # "",f,""
    # Result => ["tr-", "tr-f", "us-"]
    layouts = layouts.split(",")
    variants = variants.split(",")
    result = [f"{a}-{b}" for a, b in zip(layouts, variants)]

    return result


def save_layouts(new_layouts):
    # Result to separate string
    layouts = []
    variants = []
    for e in new_layouts:
        layout, variant = e.split("-")
        layouts.append(layout)
        variants.append(variant)

    layouts = ",".join(layouts)
    variants = ",".join(variants)

    # Save
    keyboard_layout.set_string("/Default/XkbLayout", layouts)
    keyboard_layout.set_string("/Default/XkbVariant", variants)


def add_layout(new_layout):
    # PARAM new_layout e.g.: "tr-f", "tr-", "us-"
    # Read Layouts
    new_layouts = get_layouts()

    # Add layout:
    if new_layout in new_layouts:
        return

    new_layouts.append(new_layout)

    # Save
    save_layouts(new_layouts)


def remove_layout(new_layout):
    # PARAM new_layout e.g.: "tr-f", "tr-", "us-"
    # Read Layouts
    new_layouts = get_layouts()

    # Remove layout:
    if new_layout not in new_layouts:
        return

    new_layouts.remove(new_layout)

    # Save
    save_layouts(new_layouts)


# Get System's Keyboard
def get_system_keyboards():
    layout_process = subprocess.run(
        "cat /etc/default/keyboard | grep XKBLAYOUT | tr -d '\"'",
        shell=True,
        capture_output=True,
    )
    variant_process = subprocess.run(
        "cat /etc/default/keyboard | grep XKBVARIANT | tr -d '\"'",
        shell=True,
        capture_output=True,
    )

    layouts = layout_process.stdout.decode("utf-8").rstrip().split("=")[1].split(",")
    variants = variant_process.stdout.decode("utf-8").rstrip().split("=")[1].split(",")

    for i in range(len(layouts)):
        new_layout = f"{layouts[i]}-{variants[i]}"
        add_layout(new_layout)


def refresh_panel():
    subprocess.call(["xfce4-panel", "-r"])


# PLUGIN:
def create_keyboard_plugin():
    global xfce4_panel
    # Add keyboard
    subprocess.call(["xfce4-panel", "--add=xkb"])

    keyboard_plugin = get_keyboard_plugin()
    if keyboard_plugin:
        set_keyboard_plugin_place(keyboard_plugin)

    # Display Language Name (not country)
    xfce4_panel.set_uint(f"/plugins/{keyboard_plugin}/display-name", 1)

    # Display text (not flag)
    xfce4_panel.set_uint(f"/plugins/{keyboard_plugin}/display-type", 2)

    # Enable globally (not program-wide)
    xfce4_panel.set_uint(f"/plugins/{keyboard_plugin}/group-policy", 0)


def remove_keyboard_plugin():
    global xfce4_panel

    keyboard_plugin = get_keyboard_plugin()
    if not keyboard_plugin:
        return

    # Remove plugin
    plugin_id = int(keyboard_plugin.split("-")[-1])
    xfce4_panel.reset_property(f"/plugins/{keyboard_plugin}", True)

    # Remove plugin id from list
    plugin_ids = xfce4_panel.get_arrayv("/panels/panel-1/plugin-ids")
    plugin_ids.remove(plugin_id)
    xfce4_panel.set_arrayv("/panels/panel-1/plugin-ids", plugin_ids)

    # Refresh panel
    refresh_panel()


def get_keyboard_plugin():
    for key, value in xfce4_panel.get_properties("/plugins").items():
        if type(value) is str and "xkb" == value:
            keyboard_plugin = key.split("/")[2]

            return keyboard_plugin

    return ""


def set_keyboard_plugin_place(keyboard_plugin):
    global xfce4_panel
    if keyboard_plugin == "":
        return

    plugins = xfce4_panel.get_arrayv("/panels/panel-1/plugin-ids")
    plugin_id = int(keyboard_plugin.split("-")[1])
    if plugin_id not in plugins:
        plugins.append(plugin_id)
    elif plugin_id == plugins[-2]:
        return

    plugins[-1], plugins[-2] = plugins[-2], plugins[-1]

    xfce4_panel.set_arrayv("/panels/panel-1/plugin-ids", plugins)

    refresh_panel()
