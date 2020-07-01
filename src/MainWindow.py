import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, GdkPixbuf

import WallpaperManager
import ThemeManager
import ScaleManager

class MainWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Add Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect('destroy', application.onExit)

        # Definitions
        self.defineComponents()
        self.defineVariables()

        # Put Wallpapers on a Grid
        self.addWallpapers(WallpaperManager.getWallpaperList())

        # Add Themes to Comboboxes:
        self.addThemes(ThemeManager.getThemeList())

        # Set scales to system-default:
        self.setScalingDefaults()

        # Show Screen:
        self.window.show_all()
    
    def defineComponents(self):
        # Navigation:
        self.box_headerLabels = self.builder.get_object("box_headerLabels")
        self.stk_stackPages = self.builder.get_object("stk_stackPages")
        self.btn_next = self.builder.get_object("btn_next")
        self.btn_prev = self.builder.get_object("btn_prev")
        
        # - Display Settings:
        self.lst_themes = self.builder.get_object("lst_themes")
        self.lst_windowThemes = self.builder.get_object("lst_windowThemes")
        self.cmb_theme = self.builder.get_object("cmb_theme")
        self.cmb_windowTheme = self.builder.get_object("cmb_windowTheme")
        self.flow_wallpapers = self.builder.get_object("flow_wallpapers")

        # - Scaling Settings:
        self.sli_panel = self.builder.get_object("sli_panel")
        self.sli_panelIcon = self.builder.get_object("sli_panelIcon")
        self.sli_desktopIcon = self.builder.get_object("sli_desktopIcon")

    def defineVariables(self):
        # Global stack pages:
        self.currentPage = 0
        self.pageCount = len(self.stk_stackPages.get_children())
        
        # Get bold attribute from first label in glade
        self.boldAttribute = self.box_headerLabels.get_children()[0].get_attributes()

    def changePage(self, number):
        # Set current page number
        self.currentPage = number

        # Set button sensivities
        self.btn_next.set_sensitive(not (self.currentPage == self.pageCount-1))
        self.btn_prev.set_sensitive(not (self.currentPage == 0))

        # Change current header label style
        for lbl_child in self.box_headerLabels.get_children():
            if isinstance(lbl_child, Gtk.Label):
                lbl_child.set_opacity(0.6)
                lbl_child.set_attributes(None)
        self.box_headerLabels.get_children()[self.currentPage].set_opacity(1)
        self.box_headerLabels.get_children()[self.currentPage].set_attributes(self.boldAttribute)

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
    
    # Add themes to comboboxes
    def addThemes(self, themeList):
        currentThemeIndex = 0
        currentWindowThemeIndex = 0
        currentTheme = ThemeManager.getTheme()
        currentWindowTheme = ThemeManager.getWindowTheme()

        self.lst_themes.clear()
        self.lst_windowThemes.clear()

        for i in range(len(themeList[0])):
            self.lst_themes.append([themeList[0][i]])
            if themeList[0][i] == currentTheme:
                currentThemeIndex = i
        
        for i in range(len(themeList[1])):
            self.lst_windowThemes.append([themeList[1][i]])
            if themeList[1][i] == currentWindowTheme:
                currentWindowThemeIndex = i
                
        self.cmb_theme.set_active(currentThemeIndex)
        self.cmb_windowTheme.set_active(currentWindowThemeIndex)
    
    def setScalingDefaults(self):
        self.sli_panel.set_value(ScaleManager.getPanelSize())
        self.sli_panelIcon.set_value(ScaleManager.getPanelIconSize())
        self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())


    # SIGNALS:
    # - NAVIGATION:
    def on_btn_next_clicked(self, btn):
        self.changePage(self.currentPage + 1)
    def on_btn_prev_clicked(self, btn):
        self.changePage(self.currentPage - 1)
    


    # - Wallpaper Select:
    def on_wallpaper_selected(self, flowbox, wallpaper):
        filename = str(wallpaper.get_children()[0].file)
        WallpaperManager.setWallpaper(filename)
    
    # - Theme Select:
    def on_cmb_windowTheme_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            windowTheme = model[tree_iter][0]
            ThemeManager.setWindowTheme(windowTheme)
    
    def on_cmb_theme_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            theme = model[tree_iter][0]
            ThemeManager.setTheme(theme)


    # - Scale Changed:
    def on_rb_scale100_toggled(self, btn):
        if btn.get_active():
            ScaleManager.scale(100)
    
    def on_rb_scale125_toggled(self, btn):
        if btn.get_active():
            ScaleManager.scale(125)
    
    def on_rb_scale150_toggled(self, btn):
        if btn.get_active():
            ScaleManager.scale(150)
    
    def on_rb_scale175_toggled(self, btn):
        if btn.get_active():
            ScaleManager.scale(175)
    
    def on_rb_scale200_toggled(self, btn):
        if btn.get_active():
            ScaleManager.scale(200)
    
    

    # - Panel Size Changed:
    def on_sli_panel_value_changed(self, sli):
        ScaleManager.setPanelSize(int(sli.get_value()))
    
    def on_sli_panelIcon_value_changed(self, sli):
        ScaleManager.setPanelIconSize(int(sli.get_value()))
    
    def on_sli_desktopIcon_value_changed(self, sli):
        ScaleManager.setDesktopIconSize(int(sli.get_value()))