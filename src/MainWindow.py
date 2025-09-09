#!/usr/bin/env python3

import os
import subprocess
import threading
import requests

from utils import ErrorDialog

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk

import locale
from locale import gettext as _
from locale import getlocale


import xfce.WallpaperManager as WallpaperManager
import xfce.ThemeManager as ThemeManager
import xfce.ScaleManager as ScaleManager
import xfce.KeyboardManager as KeyboardManager
# import xfce.WhiskerManager as WhiskerManager

# Translation Constants:
APPNAME = "pardus-xfce-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)

# Pardus Software Center API
PARDUS_SOFTWARE_CENTER_API = "https://apps.pardus.org.tr/api/greeter"


class MainWindow:
    def __init__(self, application):
        self.Application = application

        # Gtk Builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file(
            os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"
        )
        self.builder.connect_signals(self)

        # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        # Add Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect("destroy", self.onDestroy)

        self.user_locale = self.get_user_locale()

        self.set_css()

        # Component Definitions
        self.defineComponents()

        # Add Scaling Slider Marks
        self.addSliderMarks()

        # Put Wallpapers on a Grid
        thread = threading.Thread(
            target=self.addWallpapers, args=(WallpaperManager.getWallpaperList(),)
        )
        thread.daemon = True
        thread.start()

        # Set scales to system-default:
        self.getScalingDefaults()

        # Keyboard
        self.getKeyboardDefaults()

        # Last Variable Definitions
        self.defineVariables()

        # Show pardus software popular apps
        self.fetch_pardus_software_apps()

        # control args
        self.control_args()

        # Show Screen:
        self.window.show_all()

        # Hide widgets:
        self.hideWidgets()

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
        theme_name = (
            "{}".format(settings.get_property("gtk-theme-name")).lower().strip()
        )
        cssProvider = Gtk.CssProvider()
        if theme_name.startswith("pardus") or theme_name.startswith("adwaita"):
            cssProvider.load_from_path(
                os.path.dirname(os.path.abspath(__file__)) + "/../assets/css/all.css"
            )
        elif theme_name.startswith("adw-gtk3"):
            cssProvider.load_from_path(
                os.path.dirname(os.path.abspath(__file__)) + "/../assets/css/adw.css"
            )
        else:
            cssProvider.load_from_path(
                os.path.dirname(os.path.abspath(__file__)) + "/../assets/css/base.css"
            )
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(
            screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def defineComponents(self):
        def getUI(str):
            return self.builder.get_object(str)

        # about dialog
        self.ui_about_dialog = self.builder.get_object("ui_about_dialog")
        self.ui_about_dialog.set_program_name(_("Pardus Greeter"))
        if self.ui_about_dialog.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About Pardus Greeter"))
            about_headerbar.pack_start(
                Gtk.Image.new_from_icon_name(
                    "pardus-greeter", Gtk.IconSize.LARGE_TOOLBAR
                )
            )
            about_headerbar.show_all()
            self.ui_about_dialog.set_titlebar(about_headerbar)
        # Set version
        # If not getted from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(
                os.path.dirname(os.path.abspath(__file__)) + "/__version__"
            ).readline()
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
        self.img_lightTheme = getUI("img_lightTheme")
        self.img_darkTheme = getUI("img_darkTheme")

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

        tabTitle = self.stk_pages.get_visible_child().name
        self.lbl_headerTitle.set_text(tabTitle)

        self.ui_apps_flowbox = getUI("ui_apps_flowbox")
        self.ui_apps_error_label = getUI("ui_apps_error_label")
        self.ui_apps_stack = getUI("ui_apps_stack")

    def defineVariables(self):
        self.currentpage = 0
        self.stk_len = 0
        for row in self.stk_pages:
            self.stk_len += 1

        self.pardus_default_whisker_icon = "start-pardus"
        self.pardus_default_wallpaper_light = (
            "/usr/share/backgrounds/pardus23-0_default-light.svg"
        )
        self.pardus_default_wallpaper_dark = (
            "/usr/share/backgrounds/pardus23-0_default-dark.svg"
        )

    def set_signals(self):
        self.rb_lightTheme.connect("clicked", self.on_rb_lightTheme_clicked)
        self.rb_darkTheme.connect("clicked", self.on_rb_darkTheme_clicked)

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

        self.btn_prev.set_sensitive(self.currentpage != 0)

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

        elif theme == "pardus-xfce-dark":
            self.rb_darkTheme.set_active(True)

    def getScalingDefaults(self):
        currentScale = int((ScaleManager.getScale() / 0.25) - 4)

        self.sli_panel.set_value(ScaleManager.getPanelSize())
        self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())
        self.sli_scaling.set_value(currentScale)
        self.sli_cursor.set_value((ScaleManager.getPointerSize() / 16) - 1)

    # Keyboard Settings:
    def getKeyboardDefaults(self):
        KeyboardManager.init()

        layouts = KeyboardManager.get_layouts()

        if "tr-" in layouts:
            self.stk_trq.set_visible_child_name("remove")
        else:
            self.stk_trq.set_visible_child_name("add")

        if "tr-f" in layouts:
            self.stk_trf.set_visible_child_name("remove")
        else:
            self.stk_trf.set_visible_child_name("add")

        if "us-" in layouts:
            self.stk_en.set_visible_child_name("remove")
        else:
            self.stk_en.set_visible_child_name("add")

        self.keyboard_selection_disabling_check()

        keyboard_plugin = KeyboardManager.get_keyboard_plugin()
        self.sw_lang_indicator.set_active(len(keyboard_plugin) > 0)

    def keyboard_selection_disabling_check(self):
        self.btn_trf_remove.set_sensitive(
            self.stk_trq.get_visible_child_name() == "remove"
            or self.stk_en.get_visible_child_name() == "remove"
        )
        self.btn_trq_remove.set_sensitive(
            self.stk_trf.get_visible_child_name() == "remove"
            or self.stk_en.get_visible_child_name() == "remove"
        )
        self.btn_en_remove.set_sensitive(
            self.stk_trq.get_visible_child_name() == "remove"
            or self.stk_trf.get_visible_child_name() == "remove"
        )

    def updateProgressDots(self):
        currentpage = int(self.stk_pages.get_visible_child_name())

        for i in range(len(self.box_progressDots.get_children())):
            if i <= currentpage:
                self.box_progressDots.get_children()[i].set_visible_child_name("on")
            else:
                self.box_progressDots.get_children()[i].set_visible_child_name("off")

    def changeWindowTheme(self, isHdpi, isDark):
        if isHdpi:
            if isDark:
                GLib.idle_add(
                    ThemeManager.setWindowTheme, "pardus-xfce-dark-default-hdpi"
                )
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-default-hdpi")
        else:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-dark")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce")

    def refresh_panel(self):
        subprocess.call(["xfce4-panel", "-r"])

    def fetch_pardus_software_apps(self):
        r = requests.get(PARDUS_SOFTWARE_CENTER_API)
        print("fetched softwares:", r.json())

    def set_pardussoftware_apps(self):
        self.stream = Stream()
        self.stream.StreamGet = self.StreamGet
        self.server_response = None
        self.server = Server()
        self.server.ServerGet = self.ServerGet
        self.server.get(self.apps_url)

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
            self.ui_apps_stack.set_visible_child_name("apps")
            datas = response["greeter"]["suggestions"]
            if len(datas) > 0:
                for data in datas:
                    if self.non_tls_tried:
                        data["icon"] = data["icon"].replace("https", "http")
                    self.stream.fetch(data)
        else:
            if "tlserror" in response.keys() and not self.non_tls_tried:
                self.non_tls_tried = True
                self.apps_url = self.apps_url.replace("https", "http")
                print("trying {}".format(self.apps_url))
                self.server.get(self.apps_url)
            else:
                error_message = response["message"]
                print(error_message)
                self.ui_apps_stack.set_visible_child_name("error")
                self.ui_apps_error_label.set_text(error_message)

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
        self.stk_pages.set_visible_child_name(
            "{}".format(self.get_next_page(self.currentpage))
        )

        self.currentpage = int(self.stk_pages.get_visible_child_name())

        nextButtonPage = (
            "next" if self.get_next_page(self.currentpage) != None else "close"
        )
        self.stk_btn_next.set_visible_child_name(nextButtonPage)

        self.btn_prev.set_sensitive(self.currentpage != 0)

        # Set Header Title
        tabTitle = self.stk_pages.get_visible_child().name
        self.lbl_headerTitle.set_text(tabTitle)

        self.updateProgressDots()

    def on_btn_prev_clicked(self, btn):
        self.stk_pages.set_visible_child_name(
            "{}".format(self.get_prev_page(self.currentpage))
        )

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

    def on_rb_darkTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce-dark")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce-dark")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, True)

    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        value = int(slider.get_value()) * 0.25 + 1
        self.changeWindowTheme(
            value == 2.0, ThemeManager.getTheme() == "pardus-xfce-dark"
        )
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
        KeyboardManager.add_layout("tr-f")

        self.stk_trf.set_visible_child_name("remove")
        self.keyboard_selection_disabling_check()

    def on_btn_trf_remove_clicked(self, button):
        KeyboardManager.remove_layout("tr-f")

        self.stk_trf.set_visible_child_name("add")
        self.keyboard_selection_disabling_check()

    def on_btn_trq_add_clicked(self, button):
        KeyboardManager.add_layout("tr-")

        self.stk_trq.set_visible_child_name("remove")
        self.keyboard_selection_disabling_check()

    def on_btn_trq_remove_clicked(self, button):
        KeyboardManager.remove_layout("tr-")

        self.stk_trq.set_visible_child_name("add")
        self.keyboard_selection_disabling_check()

    def on_btn_en_add_clicked(self, button):
        KeyboardManager.add_layout("us-")

        self.stk_en.set_visible_child_name("remove")
        self.keyboard_selection_disabling_check()

    def on_btn_en_remove_clicked(self, button):
        KeyboardManager.remove_layout("us-")

        self.stk_en.set_visible_child_name("add")
        self.keyboard_selection_disabling_check()

    def on_sw_lang_indicator_state_set(self, switch, state):
        if state:
            KeyboardManager.create_keyboard_plugin()
        else:
            KeyboardManager.remove_keyboard_plugin()

    # Pardus Software Apps
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
