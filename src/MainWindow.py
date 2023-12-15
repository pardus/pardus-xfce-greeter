#!/usr/bin/env python3

import os
import subprocess
import threading

import gi

import utils
from utils import getenv, ErrorDialog

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk
import locale
from locale import gettext as _
from pathlib import Path
import apt
from pathlib import Path
import json
from locale import getlocale

# Translation Constants:
APPNAME = "pardus-xfce-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"
# SYSTEM_LANGUAGE = os.environ.get("LANG")

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)
# locale.setlocale(locale.LC_ALL, SYSTEM_LANGUAGE)


currentDesktop = ""
if "xfce" in getenv("SESSION").lower() or "xfce" in getenv("XDG_CURRENT_DESKTOP").lower():
    import xfce.WallpaperManager as WallpaperManager
    import xfce.ThemeManager as ThemeManager
    import xfce.ScaleManager as ScaleManager
    import xfce.KeyboardManager as KeyboardManager
    import xfce.WhiskerManager as WhiskerManager

    from Server import Server
    from Stream import Stream

    currentDesktop = "xfce"

# elif "gnome" in getenv("SESSION").lower() or "gnome" in getenv("XDG_CURRENT_DESKTOP").lower():
#     import gnome.WallpaperManager as WallpaperManager
#     import gnome.ThemeManager as ThemeManager
#     import gnome.ScaleManager as ScaleManager
#
#     currentDesktop = "gnome"

else:
    ErrorDialog(_("Error"), _("Your desktop environment is not supported."))
    exit(0)

autostart_file = str(Path.home()) + "/.config/autostart/tr.org.pardus.xfce-greeter.desktop"

# In live mode, the application should not welcome the user
if utils.check_live() and os.path.isfile(autostart_file):
    try:
        os.remove(autostart_file)
    except OSError:
        pass
    exit(0)

# Let the application greet the user only on the first boot
try:
    os.remove(autostart_file)
except OSError:
    pass


class MainWindow:
    def __init__(self, application):
        self.Application = application

        # Gtk Builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        # Add Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect('destroy', self.onDestroy)

        self.user_locale = self.get_user_locale()

        self.set_css()

        # Component Definitions
        self.defineComponents()

        # Add Scaling Slider Marks
        self.addSliderMarks()

        # Put Wallpapers on a Grid
        thread = threading.Thread(target=self.addWallpapers, args=(WallpaperManager.getWallpaperList(),))
        thread.daemon = True
        thread.start()

        # Set scales to system-default:
        self.getScalingDefaults()

        # Keyboard
        if currentDesktop == "xfce":
            self.getKeyboardDefaults()

        # Last Variable Definitions
        self.defineVariables()

        # set pardus-software apps
        self.set_pardussoftware_apps()

        # control args
        self.control_args()

        # Show Screen:
        self.window.show_all()

        # Hide widgets:
        self.hideWidgets()

        # control special pardus themes
        self.control_special_themes()

        # Set theme to system-default:
        self.getThemeDefaults()

        self.set_signals()

    def get_user_locale(self):
        try:
            user_locale = os.getenv("LANG").split(".")[0].split("_")[0]
        except Exception as e:
            print("{}".format(e))
            try:
                user_locale = getlocale()[0].split("_")[0]
            except Exception as e:
                print("{}".format(e))
                user_locale = "en"
        if user_locale != "tr" and user_locale != "en":
            user_locale = "en"
        return user_locale

    def set_css(self):
        settings = Gtk.Settings.get_default()
        theme_name = "{}".format(settings.get_property('gtk-theme-name')).lower().strip()
        cssProvider = Gtk.CssProvider()
        if theme_name.startswith("pardus") or theme_name.startswith("adwaita"):
            cssProvider.load_from_path(os.path.dirname(os.path.abspath(__file__)) + "/../assets/css/all.css")
        elif theme_name.startswith("adw-gtk3"):
            cssProvider.load_from_path(os.path.dirname(os.path.abspath(__file__)) + "/../assets/css/adw.css")
        else:
            cssProvider.load_from_path(os.path.dirname(os.path.abspath(__file__)) + "/../assets/css/base.css")
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def defineComponents(self):
        def getUI(str):
            return self.builder.get_object(str)

        # about dialog
        self.ui_about_dialog = self.builder.get_object("ui_about_dialog")
        self.ui_about_dialog.set_program_name(_("Pardus Greeter"))
        # Set version
        # If not getted from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(os.path.dirname(os.path.abspath(__file__)) + "/__version__").readline()
            self.ui_about_dialog.set_version(version)
        except:
            pass

        # - Navigation:
        self.lbl_headerTitle = getUI("lbl_headerTitle")
        self.stk_pages = getUI("stk_pages")
        self.stk_btn_next = getUI("stk_btn_next")
        self.btn_next = getUI("btn_next")
        self.btn_prev = getUI("btn_prev")
        self.box_progressDots = getUI("box_progressDots")

        # - Stack Pages:
        self.page_welcome = getUI("page_welcome")
        self.page_wallpaper = getUI("page_wallpaper")
        self.page_theme = getUI("page_theme")
        self.page_display = getUI("page_display")
        self.page_keyboard = getUI("page_keyboard")
        self.page_applications = getUI("page_applications")
        self.page_support = getUI("page_support")

        # FIX this solution later. Because we are not getting stack title in this gtk version.
        self.page_welcome.name = _("Welcome")
        self.page_wallpaper.name = _("Select Wallpaper")
        self.page_theme.name = _("Theme Settings")
        self.page_display.name = _("Display Settings")
        self.page_keyboard.name = _("Keyboard Settings")
        self.page_applications.name = _("Applications")
        self.page_support.name = _("Support & Community")

        # - Display Settings:
        self.lst_themes = getUI("lst_themes")
        self.lst_windowThemes = getUI("lst_windowThemes")
        self.flow_wallpapers = getUI("flow_wallpapers")
        self.rb_darkTheme = getUI("rb_darkTheme")
        self.rb_lightTheme = getUI("rb_lightTheme")
        self.special_light_rb = getUI("special_light_rb")
        self.special_dark_rb = getUI("special_dark_rb")
        self.img_lightTheme = getUI("img_lightTheme")
        self.img_darkTheme = getUI("img_darkTheme")
        self.special_light_label = getUI("special_light_label")
        self.special_light_img = getUI("special_light_img")
        self.special_dark_label = getUI("special_dark_label")
        self.special_dark_img = getUI("special_dark_img")
        self.ui_special_theme_box = getUI("ui_special_theme_box")

        # - Scaling Settings:
        self.lbl_panelSize = getUI("lbl_panelSize")
        self.lbl_desktopIconSize = getUI("lbl_desktopIconSize")
        self.sli_panel = getUI("sli_panel")
        self.sli_scaling = getUI("sli_scaling")
        self.sli_desktopIcon = getUI("sli_desktopIcon")
        self.sli_cursor = getUI("sli_cursor")

        # - Keyboard Settings:
        self.stk_trf = getUI("stk_trf")
        self.stk_trq = getUI("stk_trq")
        self.stk_en = getUI("stk_en")
        self.btn_trq_remove = getUI("btn_trq_remove")
        self.btn_trf_remove = getUI("btn_trf_remove")
        self.btn_en_remove = getUI("btn_en_remove")
        self.sw_lang_indicator = getUI("sw_lang_indicator")

        # - Shortcut Page
        self.stk_shortcuts = getUI("stk_shortcuts")
        self.stk_shortcuts.set_visible_child_name(currentDesktop)

        tabTitle = self.stk_pages.get_visible_child().name
        self.lbl_headerTitle.set_text(tabTitle)

        self.ui_apps_flowbox = getUI("ui_apps_flowbox")

    def defineVariables(self):
        self.currentpage = 0
        self.stk_len = 0
        for row in self.stk_pages:
            self.stk_len += 1

        self.special_theme_active = False

        self.pardus_default_whisker_icon = "start-pardus"
        self.pardus_default_wallpaper_light = "/usr/share/backgrounds/pardus23-0_default-light.svg"
        self.pardus_default_wallpaper_dark = "/usr/share/backgrounds/pardus23-0_default-dark.svg"

    def set_signals(self):
        self.rb_lightTheme.connect("clicked", self.on_rb_lightTheme_clicked)
        self.rb_darkTheme.connect("clicked", self.on_rb_darkTheme_clicked)
        self.special_light_rb.connect("clicked", self.on_special_light_rb_clicked)
        self.special_dark_rb.connect("clicked", self.on_special_dark_rb_clicked)

    # =========== UI Preparing functions:
    def hideWidgets(self):
        # Remove panel and desktop icon sizes if GNOME
        # if currentDesktop == "gnome":
        #     self.sli_panel.set_visible(False)
        #     self.sli_desktopIcon.set_visible(False)
        #     self.lbl_panelSize.set_visible(False)
        #     self.lbl_desktopIconSize.set_visible(False)

        # Remove Keyboard settings if not XFCE
        # if currentDesktop != "xfce":
        #     self.page_keyboard.destroy()
        #     self.box_progressDots.remove(self.box_progressDots.get_children()[0])

        self.updateProgressDots()

        self.ui_special_theme_box.set_visible(False)

        self.btn_prev.set_sensitive(self.currentpage != 0)

    def control_special_themes(self):

        theme_packages = ["pardus-yuzyil"]
        package_found = False

        try:
            cache = apt.Cache()
            for package in theme_packages:
                if cache[package].is_installed:
                    package_found = True
                    print("{} found.".format(package))
        except Exception as e:
            print("{}".format(e))

        if package_found:
            user = "{}".format(Path.home())
            user_json_file = "{}/.config/pardus/pardus-special-theme/special_theme.json".format(user)
            system_json_file = "/usr/share/pardus/pardus-special-theme/special-theme.json"

            user_json_file_ok = False
            system_json_file_ok = False

            # firstly look for user json file (setted from theme desktop file)
            try:
                if os.path.isfile(user_json_file):
                    special_json_file = json.load(open(user_json_file))
                    user_json_file_ok = True
            except Exception as e:
                print("{}".format(e))

            # if user json file is not found then look for system json file (setted from theme package file)
            if not user_json_file_ok:
                try:
                    if os.path.isfile(system_json_file):
                        special_json_file = json.load(open(system_json_file))
                        system_json_file_ok = True
                except Exception as e:
                    print("{}".format(e))

            # system json file not exists too so return
            if not user_json_file_ok and not system_json_file_ok:
                print("{}\n{}\nfiles not exists!".format(user_json_file, system_json_file))
                return

            try:
                self.special_light_name = special_json_file["light"]["name"].replace("@@desktop@@", currentDesktop)
                self.special_light_pretty_tr = special_json_file["light"]["pretty_tr"]
                self.special_light_pretty_en = special_json_file["light"]["pretty_en"]
                self.special_light_background = special_json_file["light"]["background"]
                self.special_light_image = special_json_file["light"]["image"]
                self.special_light_panel = special_json_file["light"]["panel"]

                self.special_dark_name = special_json_file["dark"]["name"].replace("@@desktop@@", currentDesktop)
                self.special_dark_pretty_tr = special_json_file["dark"]["pretty_tr"]
                self.special_dark_pretty_en = special_json_file["dark"]["pretty_en"]
                self.special_dark_background = special_json_file["dark"]["background"]
                self.special_dark_image = special_json_file["dark"]["image"]
                self.special_dark_panel = special_json_file["dark"]["panel"]
            except Exception as e:
                print("{}".format(e))
                return

            if not os.path.exists(self.special_light_background):
                print("{} not exists.".format(self.special_light_background))
                return

            if not os.path.exists(self.special_light_image):
                print("{} not exists.".format(self.special_light_image))
                return

            if not os.path.exists(self.special_light_panel):
                print("{} not exists.".format(self.special_light_panel))
                return

            if not os.path.exists(self.special_dark_background):
                print("{} not exists.".format(self.special_dark_background))
                return

            if not os.path.exists(self.special_dark_image):
                print("{} not exists.".format(self.special_dark_image))
                return

            if not os.path.exists(self.special_dark_panel):
                print("{} not exists.".format(self.special_dark_panel))
                return

            self.special_theme_active = True

            print("everything looks ok so setting theme page")
            self.img_lightTheme.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(
                os.path.dirname(os.path.abspath(__file__)) + "/../assets/theme-light.png", 233, 233))
            self.img_darkTheme.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(
                os.path.dirname(os.path.abspath(__file__)) + "/../assets/theme-dark.png", 233, 233))

            self.special_light_img.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(
                self.special_light_image, 233, 233))
            self.special_dark_img.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(
                self.special_dark_image, 233, 233))

            self.locale = self.get_locale()

            if self.locale == "tr":
                self.special_light_label.set_text("{}".format(self.special_light_pretty_tr))
                self.special_dark_label.set_text("{}".format(self.special_dark_pretty_tr))
            else:
                self.special_light_label.set_text("{}".format(self.special_light_pretty_en))
                self.special_dark_label.set_text("{}".format(self.special_dark_pretty_en))

            self.ui_special_theme_box.set_visible(True)

    def control_args(self):
        if "page" in self.Application.args.keys():
            page = self.Application.args["page"]
            self.stk_pages.set_visible_child_name("{}".format(page))
            self.currentpage = 1

    def get_locale(self):
        try:
            user_locale = os.getenv("LANG").split(".")[0].split("_")[0]
        except Exception as e:
            print("{}".format(e))
            try:
                user_locale = getlocale()[0].split("_")[0]
            except Exception as e:
                print("{}".format(e))
                user_locale = "en"
        if user_locale != "tr" and user_locale != "en":
            user_locale = "en"
        return user_locale

    def addSliderMarks(self):
        self.sli_scaling.add_mark(0, Gtk.PositionType.BOTTOM, "%100")
        self.sli_scaling.add_mark(1, Gtk.PositionType.BOTTOM, "%125")
        self.sli_scaling.add_mark(2, Gtk.PositionType.BOTTOM, "%150")
        self.sli_scaling.add_mark(3, Gtk.PositionType.BOTTOM, "%175")
        self.sli_scaling.add_mark(4, Gtk.PositionType.BOTTOM, "%200")

    # =========== Settings Functions:

    # Add wallpapers to the grid:
    def addWallpapers(self, wallpaperList):
        for i in range(len(wallpaperList)):
            # Image
            bitmap = GdkPixbuf.Pixbuf.new_from_file(wallpaperList[i])
            bitmap = bitmap.scale_simple(240, 135, GdkPixbuf.InterpType.BILINEAR)

            img_wallpaper = Gtk.Image.new_from_pixbuf(bitmap)
            img_wallpaper.img_path = wallpaperList[i]

            tooltip = wallpaperList[i]
            try:
                tooltip = os.path.basename(tooltip)
                tooltip = os.path.splitext(tooltip)[0]
                if "pardus23-0_" in tooltip:
                    tooltip = tooltip.split("pardus23-0_")[1]
                    tooltip = tooltip.replace("-", " ")
                elif "pardus23-" in tooltip and "_" in tooltip:
                    tooltip = tooltip.split("_")[1]
                    tooltip = tooltip.replace("-", " ")
            except Exception as e:
                print("{}".format(e))
                pass
            img_wallpaper.set_tooltip_text(tooltip)

            GLib.idle_add(self.flow_wallpapers.insert, img_wallpaper, -1)
            GLib.idle_add(self.flow_wallpapers.show_all)

    def getThemeDefaults(self):
        theme = ThemeManager.getTheme()
        icon_theme = ThemeManager.getIconTheme()

        if theme == "pardus-xfce":
            self.rb_lightTheme.set_active(True)
            if self.special_theme_active:
                if icon_theme == self.special_light_name:
                    self.special_light_rb.set_active(True)

        elif theme == "pardus-xfce-dark":
            self.rb_darkTheme.set_active(True)
            if self.special_theme_active:
                if icon_theme == self.special_dark_name:
                    self.special_dark_rb.set_active(True)

    def getScalingDefaults(self):
        if currentDesktop == "xfce":
            self.sli_panel.set_value(ScaleManager.getPanelSize())
            self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())

        currentScale = int((ScaleManager.getScale() / 0.25) - 4)
        self.sli_scaling.set_value(currentScale)
        self.sli_cursor.set_value((ScaleManager.getPointerSize()/16)-1)


    # Keyboard Settings:
    def getKeyboardDefaults(self):
        # We can choose the layout:
        KeyboardManager.initializeSettings()

        states = KeyboardManager.getKeyboardState()

        if states[0] == True:
            self.stk_trq.set_visible_child_name("remove")
        else:
            self.stk_trq.set_visible_child_name("add")

        if states[1] == True:
            self.stk_trf.set_visible_child_name("remove")
        else:
            self.stk_trf.set_visible_child_name("add")

        if states[2] == True:
            self.stk_en.set_visible_child_name("remove")
        else:
            self.stk_en.set_visible_child_name("add")

        self.keyboardSelectionDisablingCheck()

        keyboardPlugin = KeyboardManager.getKeyboardPlugin()
        self.sw_lang_indicator.set_active(len(keyboardPlugin) > 0)

    def keyboardSelectionDisablingCheck(self):
        # print(f"trq:{self.stk_trq.get_visible_child_name()}, trf:{self.stk_trf.get_visible_child_name()}, en:{self.stk_en.get_visible_child_name()}")
        self.btn_trf_remove.set_sensitive(
            self.stk_trq.get_visible_child_name() == "remove" or self.stk_en.get_visible_child_name() == "remove")
        self.btn_trq_remove.set_sensitive(
            self.stk_trf.get_visible_child_name() == "remove" or self.stk_en.get_visible_child_name() == "remove")
        self.btn_en_remove.set_sensitive(
            self.stk_trq.get_visible_child_name() == "remove" or self.stk_trf.get_visible_child_name() == "remove")

    def updateProgressDots(self):
        currentpage = int(self.stk_pages.get_visible_child_name())

        for i in range(len(self.box_progressDots.get_children())):
            if i <= currentpage:
                self.box_progressDots.get_children()[i].set_visible_child_name("on")
            else:
                self.box_progressDots.get_children()[i].set_visible_child_name("off")

    def changeWindowTheme(self, isHdpi, isDark):
        if currentDesktop != "xfce":
            return

        if isHdpi:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-dark-default-hdpi")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-default-hdpi")
        else:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-dark")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce")

    def refresh_panel(self):
        subprocess.call(["xfce4-panel", "-r"])

    def set_pardussoftware_apps(self):

        url = "https://apps.pardus.org.tr/api/greeter"
        self.stream = Stream()
        self.stream.StreamGet = self.StreamGet
        self.server_response = None
        self.server = Server()
        self.server.ServerGet = self.ServerGet
        self.server.get(url)

    def StreamGet(self, pixbuf, data):
        lang = f"pretty_{self.user_locale}"

        pretty_name = data[lang]
        package_name = data["name"]

        icon = Gtk.Image.new()
        icon.set_from_pixbuf(pixbuf)

        label = Gtk.Label.new()
        label.set_text("{}".format(pretty_name))
        label.set_line_wrap(True)
        label.set_max_width_chars(21)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.pack_start(icon, False, True, 0)
        box.pack_start(label, False, True, 0)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(3)
        box.set_margin_bottom(3)
        box.set_spacing(8)

        listbox = Gtk.ListBox.new()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.get_style_context().add_class("pardus-software-listbox")
        listbox.add(box)
        listbox.name = package_name

        frame = Gtk.Frame.new()
        frame.get_style_context().add_class("pardus-software-frame")
        frame.add(listbox)

        self.ui_apps_flowbox.get_style_context().add_class("pardus-software-flowbox")
        GLib.idle_add(self.ui_apps_flowbox.insert, frame, GLib.PRIORITY_DEFAULT_IDLE)

        GLib.idle_add(self.ui_apps_flowbox.show_all)

    def ServerGet(self, response):
        if "error" not in response.keys():
            datas = response["greeter"]["suggestions"]
            if len(datas) > 0:
                for data in datas:
                    self.stream.fetch(data)
        else:
            error_message = response["message"]
            # error_label = Gtk.Label("{}".format(error_message))
            print(error_message)

    # - stack prev and next page controls
    def get_next_page(self, page):
        increase = 0
        for i in range(0, self.stk_len):
            increase += 1
            if self.stk_pages.get_child_by_name("{}".format(page + increase)) != None:
                return page + increase
        return None

    def get_prev_page(self, page):
        increase = 0
        for i in range(0, self.stk_len):
            increase += -1
            if self.stk_pages.get_child_by_name("{}".format(page + increase)) != None:
                return page + increase
        return None

    # =========== SIGNALS:    
    def onDestroy(self, b):
        self.window.get_application().quit()

    def on_ui_about_button_clicked(self, button):
        self.ui_about_dialog.run()
        self.ui_about_dialog.hide()

    # - NAVIGATION:
    def on_btn_next_clicked(self, btn):
        self.stk_pages.set_visible_child_name("{}".format(self.get_next_page(self.currentpage)))

        self.currentpage = int(self.stk_pages.get_visible_child_name())

        nextButtonPage = "next" if self.get_next_page(self.currentpage) != None else "close"
        self.stk_btn_next.set_visible_child_name(nextButtonPage)

        self.btn_prev.set_sensitive(self.currentpage != 0)

        # Set Header Title
        tabTitle = self.stk_pages.get_visible_child().name
        self.lbl_headerTitle.set_text(tabTitle)

        self.updateProgressDots()

    def on_btn_prev_clicked(self, btn):
        self.stk_pages.set_visible_child_name("{}".format(self.get_prev_page(self.currentpage)))

        self.currentpage = int(self.stk_pages.get_visible_child_name())

        self.stk_btn_next.set_visible_child_name("next")
        self.btn_prev.set_sensitive(self.currentpage != 0)

        # Set Header Title
        tabTitle = self.stk_pages.get_visible_child().name
        self.lbl_headerTitle.set_text(tabTitle)

        self.updateProgressDots()

    # - Wallpaper Select:
    def on_wallpaper_selected(self, flowbox, wallpaper):
        filename = str(wallpaper.get_children()[0].img_path)
        WallpaperManager.setWallpaper(filename)

    # - Theme Selection:
    def on_rb_lightTheme_clicked(self, rb):
        if rb.get_active():

            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, False)

            if self.special_theme_active:
                # Wallpaper
                WallpaperManager.setWallpaper(self.pardus_default_wallpaper_light)

                # Whisker
                GLib.idle_add(WhiskerManager.set, "button-icon", self.pardus_default_whisker_icon)
                GLib.idle_add(WhiskerManager.saveFile)

                # Refresh panel
                GLib.idle_add(self.refresh_panel)

    def on_rb_darkTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce-dark")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce-dark")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, True)

            if self.special_theme_active:
                # Wallpaper
                WallpaperManager.setWallpaper(self.pardus_default_wallpaper_dark)

                # Whisker
                GLib.idle_add(WhiskerManager.set, "button-icon", self.pardus_default_whisker_icon)
                GLib.idle_add(WhiskerManager.saveFile)

                # Refresh panel
                GLib.idle_add(self.refresh_panel)

    def on_special_light_rb_clicked(self, rb):
        print("on_special_light_rb_clicked")
        if rb.get_active():
            print("on_special_light_rb_clicked active")
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce-yuzyil")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, False)

            # Wallpaper
            WallpaperManager.setWallpaper(self.special_light_background)

            # Whisker
            GLib.idle_add(WhiskerManager.set, "button-icon", self.special_light_panel)
            GLib.idle_add(WhiskerManager.saveFile)

            # Refresh panel
            GLib.idle_add(self.refresh_panel)

    def on_special_dark_rb_clicked(self, rb):
        print("on_special_dark_rb_clicked")
        if rb.get_active():
            print("on_special_dark_rb_clicked active")
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce-dark")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce-yuzyil-dark")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, True)

            # Wallpaper
            WallpaperManager.setWallpaper(self.special_dark_background)

            # Whisker
            GLib.idle_add(WhiskerManager.set, "button-icon", self.special_dark_panel)
            GLib.idle_add(WhiskerManager.saveFile)

            # Refresh panel
            GLib.idle_add(self.refresh_panel)

    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        value = int(slider.get_value()) * 0.25 + 1
        self.changeWindowTheme(value == 2.0, ThemeManager.getTheme() == "pardus-xfce-dark")
        ScaleManager.setScale(value)

    def on_sli_scaling_format_value(self, sli, value):
        return f"%{int(value * 25 + 100)}"

    # - Panel Size Changed:
    def on_sli_panel_value_changed(self, sli):
        ScaleManager.setPanelSize(int(sli.get_value()))

    def on_sli_desktopIcon_value_changed(self, sli):
        ScaleManager.setDesktopIconSize(int(sli.get_value()))

    def on_sli_cursor_format_value(self, sli, value):
        return f"{int(value + 1) * 16}"

    def on_sli_cursor_value_changed(self, sli):
        ScaleManager.setPointerSize(int(sli.get_value() + 1) * 16)

    # - Keyboard Layout Changed:
    def on_btn_trf_add_clicked(self, button):
        KeyboardManager.setTurkishF(True)
        self.stk_trf.set_visible_child_name("remove")
        self.keyboardSelectionDisablingCheck()

    def on_btn_trf_remove_clicked(self, button):
        KeyboardManager.setTurkishF(False)
        self.stk_trf.set_visible_child_name("add")
        self.keyboardSelectionDisablingCheck()

    def on_btn_trq_add_clicked(self, button):
        KeyboardManager.setTurkishQ(True)
        self.stk_trq.set_visible_child_name("remove")
        self.keyboardSelectionDisablingCheck()

    def on_btn_trq_remove_clicked(self, button):
        KeyboardManager.setTurkishQ(False)
        self.stk_trq.set_visible_child_name("add")
        self.keyboardSelectionDisablingCheck()

    def on_btn_en_add_clicked(self, button):
        KeyboardManager.setEnglish(True)
        self.stk_en.set_visible_child_name("remove")
        self.keyboardSelectionDisablingCheck()

    def on_btn_en_remove_clicked(self, button):
        KeyboardManager.setEnglish(False)
        self.stk_en.set_visible_child_name("add")
        self.keyboardSelectionDisablingCheck()

    def on_sw_lang_indicator_state_set(self, switch, state):
        if state:
            KeyboardManager.createKeyboardPlugin()
        else:
            KeyboardManager.removeKeyboardPlugin()

    def on_ui_apps_flowbox_child_activated(self, flow_box, child):
        package_name = child.get_children()[0].get_children()[0].name
        try:
            subprocess.Popen(["pardus-software", "-d", package_name])
        except Exception as e:
            ErrorDialog(_("Error"), "{}".format(e))

    def on_ui_pardus_software_button_clicked(self, button):
        try:
            subprocess.Popen(["pardus-software"])
        except Exception as e:
            ErrorDialog(_("Error"), "{}".format(e))

    def on_ui_pardus_tweaks_button_clicked(self, button):
        try:
            subprocess.Popen(["pardus-xfce-tweaks"])
        except Exception as e:
            ErrorDialog(_("Error"), "{}".format(e))
