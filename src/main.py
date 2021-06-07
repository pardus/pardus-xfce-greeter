#!/usr/bin/env python3

import sys
import gi
import utils
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from MainWindow import MainWindow

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="tr.org.pardus.kaptan", **kwargs)
        self.window = None
    
    def do_activate(self):
        self.window = MainWindow(self)


if __name__ == "__main__":
    if utils.check_live():
        exit(0)
    app = Application()
    app.run(sys.argv)
