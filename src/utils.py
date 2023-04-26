#!/usr/bin/env python3

import os

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def getenv(name):
    if name in os.environ:
        return os.environ[name]
    else:
        return ""


def check_live():
    f = open("/proc/cmdline", "r").read()
    return "boot=live" in f


class Dialog(Gtk.MessageDialog):
    def __init__(self, style, buttons, title, text, text2=None, parent=None):
        Gtk.MessageDialog.__init__(self, parent, 0, style, buttons)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title(title)
        self.set_markup(text)

    def show(self):
        try:
            response = self.run()
        finally:
            self.destroy()


def ErrorDialog(*args):
    dialog = Dialog(Gtk.MessageType.ERROR, Gtk.ButtonsType.NONE, *args)
    dialog.add_button("OK", Gtk.ResponseType.OK)
    return dialog.show()
