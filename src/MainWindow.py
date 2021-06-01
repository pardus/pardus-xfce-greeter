import os
import gi
from utils import getenv, ErrorDialog

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

import locale
from locale import gettext as tr

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
    currentDesktop = "xfce"
elif "gnome" in getenv("SESSION").lower() or "gnome" in getenv("XDG_CURRENT_DESKTOP").lower():
    import gnome.WallpaperManager as WallpaperManager
    import gnome.ThemeManager as ThemeManager
    import gnome.ScaleManager as ScaleManager
    currentDesktop = "gnome"
else:
    ErrorDialog("Error","Your desktop environment is not supported yet.")
    exit(0)

class MainWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        # Add Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect('destroy', application.onExit)

        # Definitions
        self.defineComponents()
        self.defineVariables()

        # Hide some settings if different DE
        self.addWidgetSettings()

        # Put Wallpapers on a Grid
        self.addWallpapers(WallpaperManager.getWallpaperList())

        # Set scales to system-default:
        self.setScalingDefaults()

        # Show Screen:
        self.window.show_all()

        # Hide widgets:
        self.hideWidgets()

    def hideWidgets(self):
        self.changePage(0)

        # Remove panel and desktop icon sizes
        if currentDesktop == "gnome":
            self.sli_panel.set_visible(False)
            self.sli_desktopIcon.set_visible(False)
            self.lbl_panelSize.set_visible(False)
            self.lbl_desktopIconSize.set_visible(False)

    def defineComponents(self):
        # Navigation:
        self.stk_stackPages = self.builder.get_object("stk_stackPages")
        self.btn_next = self.builder.get_object("btn_next")
        self.btn_prev = self.builder.get_object("btn_prev")
        
        # - Display Settings:
        self.lst_themes = self.builder.get_object("lst_themes")
        self.lst_windowThemes = self.builder.get_object("lst_windowThemes")
        self.flow_wallpapers = self.builder.get_object("flow_wallpapers")

        # - Scaling Settings:
        self.lbl_panelSize = self.builder.get_object("lbl_panelSize")
        self.lbl_desktopIconSize = self.builder.get_object("lbl_desktopIconSize")
        self.sli_panel = self.builder.get_object("sli_panel")
        self.sli_scaling = self.builder.get_object("sli_scaling")
        self.sli_desktopIcon = self.builder.get_object("sli_desktopIcon")

    def defineVariables(self):
        # Global stack pages:
        self.currentPage = 0
        self.pageCount = len(self.stk_stackPages.get_children())
    
    def addWidgetSettings(self):        
        # Add scaling marks
        self.sli_scaling.add_mark(1, Gtk.PositionType.BOTTOM, "%100")
        self.sli_scaling.add_mark(1.25, Gtk.PositionType.BOTTOM, "%125")
        self.sli_scaling.add_mark(1.5, Gtk.PositionType.BOTTOM, "%150")
        self.sli_scaling.add_mark(1.75, Gtk.PositionType.BOTTOM, "%175")
        self.sli_scaling.add_mark(2, Gtk.PositionType.BOTTOM, "%200")        


    def changePage(self, number):
        # Set current page number
        self.currentPage = number

        # Set button sensivities
        self.btn_next.set_sensitive(not (self.currentPage == self.pageCount-1))
        self.btn_prev.set_sensitive(not (self.currentPage == 0))

        # Change current stack page
        self.stk_stackPages.set_visible_child_name(f"page{number}")
    
    

    # FUNCTIONS ABOUT PAGES

    # Add wallpapers to the grid:
    def addWallpapers(self, wallpaperList):
        for i in range(len(wallpaperList)):            
            bitmap = GdkPixbuf.Pixbuf.new_from_file(wallpaperList[i])
            bitmap = bitmap.scale_simple(240, 135, GdkPixbuf.InterpType.BILINEAR)

            img_wallpaper = Gtk.Image.new_from_pixbuf(bitmap)
            img_wallpaper.file = wallpaperList[i]

            self.flow_wallpapers.insert(img_wallpaper, -1)
        self.flow_wallpapers.show_all()
    
    def setScalingDefaults(self):
        if currentDesktop == "xfce":
            self.sli_panel.set_value(ScaleManager.getPanelSize())
            self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())
        
        currentScale = ScaleManager.getScale()
        self.sli_scaling.set_value(currentScale)

    # SIGNALS:
    # - NAVIGATION:
    def on_btn_next_clicked(self, btn):
        if self.currentPage < self.pageCount:
            self.changePage(self.currentPage + 1)
    def on_btn_prev_clicked(self, btn):
        if self.currentPage > 0:
            self.changePage(self.currentPage - 1)
    


    # - Wallpaper Select:
    def on_wallpaper_selected(self, flowbox, wallpaper):
        filename = str(wallpaper.get_children()[0].file)
        WallpaperManager.setWallpaper(filename)

    # - Theme Selection:
    def on_rb_lightTheme_toggled(self, rb):
        if rb.get_active():
            ThemeManager.setTheme("Adwaita")
    
    def on_rb_darkTheme_toggled(self, rb):
        if rb.get_active():
            ThemeManager.setTheme("Adwaita-dark")


    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        ScaleManager.setScale(float(slider.get_value()))
    
    def on_sli_scaling_format_value(self, sli, value):
        return f"%{int(value*100)}"
    

    # - Panel Size Changed:
    def on_sli_panel_value_changed(self, sli):
        ScaleManager.setPanelSize(int(sli.get_value()))
    
    def on_sli_desktopIcon_value_changed(self, sli):
        ScaleManager.setDesktopIconSize(int(sli.get_value()))