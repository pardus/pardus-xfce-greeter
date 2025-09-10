#!/usr/bin/env python3

import os
import subprocess
import requests

from utils import ErrorDialog

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk, Gio

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
        self.application = application

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
        self.window.connect("destroy", self.on_destroy)

        self.user_locale = self.get_user_locale()

        self.set_css()

        # Component Definitions
        self.define_components()

        # Add Scaling Slider Marks
        self.add_slider_marks()

        # Put Wallpapers on a Grid
        get_wallpapers_task = Gio.Task.new()
        get_wallpapers_task.run_in_thread(self.get_wallpapers)

        # Set scales to system-default:
        self.get_scaling_defaults()

        # Keyboard
        self.get_keyboard_defaults()

        # Last Variable Definitions
        self.define_variables()

        # Show pardus software popular apps
        fetch_apps_task = Gio.Task.new()
        fetch_apps_task.run_in_thread(self.fetch_pardus_software_apps)

        # control args
        self.control_args()

        # Show Screen:
        self.window.show_all()

        # Hide widgets:
        self.hide_widgets()

        # Set theme to system-default:
        self.get_theme_defaults()

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

    def define_components(self):
        def UI(str):
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
        self.lbl_headerTitle = UI("lbl_headerTitle")
        self.stk_pages = UI("stk_pages")
        self.stk_btn_next = UI("stk_btn_next")
        self.btn_next = UI("btn_next")
        self.btn_prev = UI("btn_prev")
        self.box_progressDots = UI("box_progressDots")

        # - Stack Pages:
        self.page_welcome = UI("page_welcome")
        self.page_wallpaper = UI("page_wallpaper")
        self.page_theme = UI("page_theme")
        self.page_display = UI("page_display")
        self.page_keyboard = UI("page_keyboard")
        self.page_applications = UI("page_applications")
        self.page_support = UI("page_support")

        # FIX this solution later. Because we are not getting stack title in this gtk version.
        self.page_welcome.name = _("Welcome")
        self.page_wallpaper.name = _("Select Wallpaper")
        self.page_theme.name = _("Theme Settings")
        self.page_display.name = _("Display Settings")
        self.page_keyboard.name = _("Keyboard Settings")
        self.page_applications.name = _("Applications")
        self.page_support.name = _("Support & Community")

        # - Display Settings:
        self.lst_themes = UI("lst_themes")
        self.lst_windowThemes = UI("lst_windowThemes")
        self.flow_wallpapers = UI("flow_wallpapers")
        self.rb_darkTheme = UI("rb_darkTheme")
        self.rb_lightTheme = UI("rb_lightTheme")
        self.img_lightTheme = UI("img_lightTheme")
        self.img_darkTheme = UI("img_darkTheme")

        # - Scaling Settings:
        self.lbl_panelSize = UI("lbl_panelSize")
        self.lbl_desktopIconSize = UI("lbl_desktopIconSize")
        self.sli_panel = UI("sli_panel")
        self.sli_scaling = UI("sli_scaling")
        self.sli_desktopIcon = UI("sli_desktopIcon")
        self.sli_cursor = UI("sli_cursor")

        # - Keyboard Settings:
        self.stk_trf = UI("stk_trf")
        self.stk_trq = UI("stk_trq")
        self.stk_en = UI("stk_en")
        self.btn_trq_remove = UI("btn_trq_remove")
        self.btn_trf_remove = UI("btn_trf_remove")
        self.btn_en_remove = UI("btn_en_remove")
        self.sw_lang_indicator = UI("sw_lang_indicator")

        tabTitle = self.stk_pages.get_visible_child().name
        self.lbl_headerTitle.set_text(tabTitle)

        self.ui_apps_flowbox = UI("ui_apps_flowbox")
        self.ui_apps_error_label = UI("ui_apps_error_label")
        self.ui_apps_stack = UI("ui_apps_stack")

    def define_variables(self):
        self.currentpage = 0
        self.stk_len = 0
        for row in self.stk_pages:
            self.stk_len += 1

        self.pardus_default_whisker_icon = "start-pardus"
        self.pardus_default_wallpaper_light = (
            "/usr/share/backgrounds/pardus25-0_default-light.svg"
        )
        self.pardus_default_wallpaper_dark = (
            "/usr/share/backgrounds/pardus25-0_default-dark.svg"
        )

    def set_signals(self):
        self.rb_lightTheme.connect("clicked", self.on_rb_lightTheme_clicked)
        self.rb_darkTheme.connect("clicked", self.on_rb_darkTheme_clicked)

    # =========== UI Preparing functions:
    def hide_widgets(self):
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

        self.update_progress_dots()

        self.btn_prev.set_sensitive(self.currentpage != 0)

    def control_args(self):
        if "page" in self.application.args.keys():
            page = self.application.args["page"]
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

    def add_slider_marks(self):
        self.sli_scaling.add_mark(0, Gtk.PositionType.BOTTOM, "%100")
        self.sli_scaling.add_mark(1, Gtk.PositionType.BOTTOM, "%125")
        self.sli_scaling.add_mark(2, Gtk.PositionType.BOTTOM, "%150")
        self.sli_scaling.add_mark(3, Gtk.PositionType.BOTTOM, "%175")
        self.sli_scaling.add_mark(4, Gtk.PositionType.BOTTOM, "%200")

    # =========== Settings Functions:

    # Add wallpapers to the grid:
    def get_wallpapers(self, task, source_object, task_data, cancellable):
        wallpaper_paths = WallpaperManager.get_wallpapers()

        for w in wallpaper_paths:
            self.append_wallpaper(w)

    def append_wallpaper(self, path):
        # Image
        bitmap = GdkPixbuf.Pixbuf.new_from_file(path)
        bitmap = bitmap.scale_simple(240, 135, GdkPixbuf.InterpType.BILINEAR)

        img_wallpaper = Gtk.Image.new_from_pixbuf(bitmap)
        img_wallpaper.img_path = path

        tooltip = path.split("pardus23-0_")[-1].split("pardus25-0_")[-1]
        img_wallpaper.set_tooltip_text(tooltip)

        self.flow_wallpapers.add(img_wallpaper)
        self.flow_wallpapers.show_all()

    def add_wallpapers(self, wallpaperList):
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

    def get_theme_defaults(self):
        theme = ThemeManager.getTheme()
        icon_theme = ThemeManager.getIconTheme()

        if theme == "pardus-xfce":
            self.rb_lightTheme.set_active(True)

        elif theme == "pardus-xfce-dark":
            self.rb_darkTheme.set_active(True)

    def get_scaling_defaults(self):
        currentScale = int((ScaleManager.getScale() / 0.25) - 4)

        self.sli_panel.set_value(ScaleManager.getPanelSize())
        self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())
        self.sli_scaling.set_value(currentScale)
        self.sli_cursor.set_value((ScaleManager.getPointerSize() / 16) - 1)

    # Keyboard Settings:
    def get_keyboard_defaults(self):
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

    def update_progress_dots(self):
        currentpage = int(self.stk_pages.get_visible_child_name())

        for i in range(len(self.box_progressDots.get_children())):
            if i <= currentpage:
                self.box_progressDots.get_children()[i].set_visible_child_name("on")
            else:
                self.box_progressDots.get_children()[i].set_visible_child_name("off")

    def change_window_theme(self, isHdpi, isDark):
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

    def fetch_pardus_software_apps(self, task, source_object, task_data, cancellable):
        try:
            r = requests.get(PARDUS_SOFTWARE_CENTER_API)
        except requests.exceptions.SSLError as e:
            print(f"SSL Error: {e}")
            print("Trying http url...")

            http_url = PARDUS_SOFTWARE_CENTER_API.replace("https", "http")
            try:
                r = requests.get(http_url)
            except Exception as e:
                print(_("Couldn't fetch suggested apps from pardus software."))
                print(e)

                self.ui_apps_stack.set_visible_child_name("error")
                self.ui_apps_error_label.set_text(
                    _("Couldn't fetch suggested apps from pardus software.")
                )
            return
        except Exception as e:
            print(_("Couldn't fetch suggested apps from pardus software."))
            print(e)

            self.ui_apps_stack.set_visible_child_name("error")
            self.ui_apps_error_label.set_text(
                _("Couldn't fetch suggested apps from pardus software.")
            )
            return

        # Failed api return
        json_response = r.json()
        if r.status_code != 200:
            print("Server returned failure:")
            print(json_response)
            self.ui_apps_stack.set_visible_child_name("error")
            self.ui_apps_error_label.set_text(
                _("Couldn't fetch suggested apps from pardus software.")
            )
            return

        suggested_apps = json_response["greeter"]["suggestions"]

        for app in suggested_apps:
            self.append_app_to_suggested_flowbox(app)

    def append_app_to_suggested_flowbox(self, app):
        lang = f"pretty_{self.user_locale}"

        name = app[lang]
        package_name = app["name"]
        icon_url = app["icon"]

        box = Gtk.HBox(
            spacing=8,
            margin_start=8,
            margin_end=8,
            margin_top=3,
            margin_bottom=3,
            halign="start",
        )

        # Fetch Image file from url:
        img_file = Gio.File.new_for_uri(icon_url)
        suffix = icon_url.split(".")[-1]
        (is_success, data, _etag) = img_file.load_contents()
        if is_success:
            tmp_filepath = f"/tmp/par-gr-{package_name}.{suffix}"
            tmp_img_file = Gio.File.new_for_path(tmp_filepath)

            is_success = img_file.copy(tmp_img_file, Gio.FileCopyFlags.OVERWRITE)
            if is_success:
                icon = Gtk.Image.new_from_file(tmp_filepath)
                box.add(icon)

        # Add Label
        label = Gtk.Label.new()
        label.set_text(f"{name}")
        label.set_line_wrap(True)
        label.set_max_width_chars(21)
        box.add(label)

        button = Gtk.Button()
        button.connect("clicked", self.on_btn_suggested_app_clicked, package_name)
        button.add(box)

        self.ui_apps_flowbox.add(button)
        self.ui_apps_flowbox.show_all()

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
    def on_destroy(self, b):
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

        self.update_progress_dots()

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

        self.update_progress_dots()

    # - Wallpaper Select:
    def on_wallpaper_selected(self, flowbox, wallpaper):
        filename = str(wallpaper.get_children()[0].img_path)
        WallpaperManager.set_wallpaper(filename)

    # - Theme Selection:
    def on_rb_lightTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce")

            # Window Theme
            self.change_window_theme(ScaleManager.getScale() == 2.0, False)

    def on_rb_darkTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce-dark")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce-dark")

            # Window Theme
            self.change_window_theme(ScaleManager.getScale() == 2.0, True)

    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        value = int(slider.get_value()) * 0.25 + 1
        self.change_window_theme(
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
    def on_btn_suggested_app_clicked(self, btn, package_name):
        try:
            subprocess.Popen(["pardus-software", "-d", package_name])
        except Exception as e:
            ErrorDialog(_("Error"), "{}".format(e))

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
