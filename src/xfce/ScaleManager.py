#!/usr/bin/env python3

import subprocess

import gi

gi.require_version('Xfconf', '0')
from gi.repository import Xfconf

Xfconf.init()
xsettings = Xfconf.Channel.new("xsettings")
xfce4_panel = Xfconf.Channel.new("xfce4-panel")
xfce4_desktop = Xfconf.Channel.new("xfce4-desktop")

defaultDPI = 96


def setScale(scaling_factor):
    newDPI = defaultDPI * scaling_factor
    xsettings.set_int("/Xft/DPI", int(newDPI))

    subprocess.call([
        "xfce4-panel",
        "-r"
    ])


def setPanelSize(px):
    xfce4_panel.set_uint("/panels/panel-1/size", px)


def setPanelIconSize(px):
    xfce4_panel.set_uint("/panels/panel-1/icon-size", px)


def setDesktopIconSize(px):
    xfce4_desktop.set_uint("/desktop-icons/icon-size", px)


def setPointerSize(px):
    current_theme = xsettings.get_string("/Gtk/CursorThemeName", "Adwaita")
    xsettings.set_int("/Gtk/CursorThemeSize", px)
    xsettings.set_string("/Gtk/CursorThemeName", "Adwaita")
    xsettings.set_string("/Gtk/CursorThemeName", current_theme)


def getScale():
    dpi = xsettings.get_int("/Xft/DPI", defaultDPI)
    return float(dpi / defaultDPI)


def getPanelSize():
    return xfce4_panel.get_uint("/panels/panel-1/size", 34)


def getPanelIconSize():
    return xfce4_panel.get_uint("/panels/panel-1/icon-size", 24)


def getDesktopIconSize():
    return xfce4_desktop.get_uint("/desktop-icons/icon-size", 42)


def getPointerSize():
    return xsettings.get_int("/Gtk/CursorThemeSize", 16)
