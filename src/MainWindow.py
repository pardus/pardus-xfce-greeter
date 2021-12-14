import os, threading
import subprocess
import gi
from utils import getenv, ErrorDialog

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gio

import locale
from locale import gettext as tr

from pathlib import Path

# Translation Constants:
APPNAME = "pardus-welcome"
TRANSLATIONS_PATH = "/usr/share/locale"
SYSTEM_LANGUAGE = os.environ.get("LANG")

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)
locale.setlocale(locale.LC_ALL, SYSTEM_LANGUAGE)


currentDesktop = ""
if "xfce" in getenv("SESSION").lower() or "xfce" in getenv("XDG_CURRENT_DESKTOP").lower():
    import xfce.WallpaperManager as WallpaperManager
    import xfce.ThemeManager as ThemeManager
    import xfce.ScaleManager as ScaleManager
    import xfce.KeyboardManager as KeyboardManager
    import xfce.PanelManager as PanelManager
    currentDesktop = "xfce"
elif "gnome" in getenv("SESSION").lower() or "gnome" in getenv("XDG_CURRENT_DESKTOP").lower():
    import gnome.WallpaperManager as WallpaperManager
    import gnome.ThemeManager as ThemeManager
    import gnome.ScaleManager as ScaleManager
    currentDesktop = "gnome"
else:
    ErrorDialog("Error","Your desktop environment is not supported yet.")
    exit(0)

try:
    os.remove(str(Path.home()) + "/.config/autostart/tr.org.pardus.welcome.desktop")
except OSError:
    pass

class MainWindow:
    def __init__(self, application):
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

        # Definitions
        self.defineComponents()
        self.defineVariables()

        # Add Scaling Slider Marks
        self.addSliderMarks()

        # Put Wallpapers on a Grid
        thread = threading.Thread(target=self.addWallpapers, args=(WallpaperManager.getWallpaperList(),))
        thread.daemon = True
        thread.start()

        # Set theme to system-default:
        self.getThemeDefaults()

        # Set scales to system-default:
        self.getScalingDefaults()

        # Keyboard
        if currentDesktop == "xfce":
            self.getKeyboardDefaults()

        # Show Screen:
        self.window.show_all()

        # Hide widgets:
        self.hideWidgets()

    def defineComponents(self):
        # - Navigation:
        self.lbl_headerTitle = self.builder.get_object("lbl_headerTitle")
        self.nb_pages = self.builder.get_object("nb_pages")
        self.stk_btn_next = self.builder.get_object("stk_btn_next")
        self.btn_next = self.builder.get_object("btn_next")
        self.btn_prev = self.builder.get_object("btn_prev")
        self.box_progressDots = self.builder.get_object("box_progressDots")
        
        # - Display Settings:
        self.lst_themes = self.builder.get_object("lst_themes")
        self.lst_windowThemes = self.builder.get_object("lst_windowThemes")
        self.flow_wallpapers = self.builder.get_object("flow_wallpapers")
        self.rb_darkTheme = self.builder.get_object("rb_darkTheme")
        self.rb_lightTheme = self.builder.get_object("rb_lightTheme")

        # - Scaling Settings:
        self.lbl_panelSize = self.builder.get_object("lbl_panelSize")
        self.lbl_desktopIconSize = self.builder.get_object("lbl_desktopIconSize")
        self.sli_panel = self.builder.get_object("sli_panel")
        self.sli_scaling = self.builder.get_object("sli_scaling")
        self.sli_desktopIcon = self.builder.get_object("sli_desktopIcon")

        # - Keyboard Settings:
        self.stk_trf = self.builder.get_object("stk_trf")
        self.stk_trq = self.builder.get_object("stk_trq")
        self.stk_en = self.builder.get_object("stk_en")
        self.btn_trq_remove = self.builder.get_object("btn_trq_remove")
        self.btn_trf_remove = self.builder.get_object("btn_trf_remove")
        self.btn_en_remove = self.builder.get_object("btn_en_remove")
        self.sw_lang_indicator = self.builder.get_object("sw_lang_indicator")

        # - Stack Pages:
        self.page_keyboardSettings = self.builder.get_object("page_keyboardSettings")

        tabTitle = self.nb_pages.get_tab_label_text(self.nb_pages.get_nth_page(self.nb_pages.get_current_page()))
        self.lbl_headerTitle.set_text(tabTitle)

    def defineVariables(self):
        pass
    
    # =========== UI Preparing functions:
    def hideWidgets(self):
        # Remove panel and desktop icon sizes if GNOME
        if currentDesktop == "gnome":
            self.sli_panel.set_visible(False)
            self.sli_desktopIcon.set_visible(False)
            self.lbl_panelSize.set_visible(False)
            self.lbl_desktopIconSize.set_visible(False)
        
        # Remove Keyboard settings if not XFCE
        if currentDesktop != "xfce":
            self.nb_pages.detach_tab(self.page_keyboardSettings)
            self.box_progressDots.remove(self.box_progressDots.get_children()[0])

        self.updateProgressDots()

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

            GLib.idle_add(self.flow_wallpapers.insert, img_wallpaper, -1)
            GLib.idle_add(self.flow_wallpapers.show_all)
    
    def getThemeDefaults(self):
        theme = ThemeManager.getTheme()

        if theme == "pardus":
            self.rb_lightTheme.set_active(True)
        elif theme == "pardus-dark":
            self.rb_darkTheme.set_active(True)

    def getScalingDefaults(self):
        if currentDesktop == "xfce":
            self.sli_panel.set_value(ScaleManager.getPanelSize())
            self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())
        
        currentScale = int((ScaleManager.getScale() / 0.25) - 4)
        self.sli_scaling.set_value(currentScale)
    
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
        self.btn_trf_remove.set_sensitive(self.stk_trq.get_visible_child_name() == "remove" or self.stk_en.get_visible_child_name() == "remove")
        self.btn_trq_remove.set_sensitive(self.stk_trf.get_visible_child_name() == "remove" or self.stk_en.get_visible_child_name() == "remove")
        self.btn_en_remove.set_sensitive(self.stk_trq.get_visible_child_name() == "remove" or self.stk_trf.get_visible_child_name() == "remove")
    
    def updateProgressDots(self):
        currentPage = self.nb_pages.get_current_page()

        for i in range(len(self.box_progressDots.get_children())):
            if i <= currentPage:
                self.box_progressDots.get_children()[i].set_visible_child_name("on")
            else:
                self.box_progressDots.get_children()[i].set_visible_child_name("off")
    
    def changeWindowTheme(self, isHdpi, isDark):
        if currentDesktop != "xfce":
            return

        if isHdpi:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-dark-default-hdpi")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-default-hdpi")
        else:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-dark-default")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-default")

    # =========== SIGNALS:    
    def onDestroy(self, b):
        self.window.get_application().quit()

    # - NAVIGATION:
    def on_btn_next_clicked(self, btn):
        self.nb_pages.next_page()

        nextButtonPage = "next" if self.nb_pages.get_current_page() != len(self.nb_pages.get_children())-1 else "close"
        self.stk_btn_next.set_visible_child_name(nextButtonPage)

        self.btn_prev.set_sensitive( self.nb_pages.get_current_page() != 0 )

        # Set Header Title
        tabTitle = self.nb_pages.get_tab_label_text(self.nb_pages.get_nth_page(self.nb_pages.get_current_page()))
        self.lbl_headerTitle.set_text(tabTitle)

        self.updateProgressDots()
    
    def on_btn_prev_clicked(self, btn):
        self.nb_pages.prev_page()

        nextButtonPage = "next" if self.nb_pages.get_current_page() != len(self.nb_pages.get_children())-1 else "close"
        self.stk_btn_next.set_visible_child_name(nextButtonPage)
        self.btn_prev.set_sensitive( self.nb_pages.get_current_page() != 0 )

        # Set Header Title
        tabTitle = self.nb_pages.get_tab_label_text(self.nb_pages.get_nth_page(self.nb_pages.get_current_page()))
        self.lbl_headerTitle.set_text(tabTitle)

        self.updateProgressDots()


    # - Wallpaper Select:
    def on_wallpaper_selected(self, flowbox, wallpaper):
        filename = str(wallpaper.get_children()[0].img_path)
        WallpaperManager.setWallpaper(filename)


    # - Theme Selection:
    def on_rb_lightTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, False)
    
    def on_rb_darkTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-dark")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-dark")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, True)


    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        value = int(slider.get_value()) * 0.25 + 1
        self.changeWindowTheme(value == 2.0, ThemeManager.getTheme() == "pardus-dark")
        ScaleManager.setScale(value)
    
    def on_sli_scaling_format_value(self, sli, value):
        return f"%{int(value * 25 + 100)}"
    

    # - Panel Size Changed:
    def on_sli_panel_value_changed(self, sli):
        ScaleManager.setPanelSize(int(sli.get_value()))
    
    def on_sli_desktopIcon_value_changed(self, sli):
        ScaleManager.setDesktopIconSize(int(sli.get_value()))


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
    
