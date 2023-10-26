#!/usr/bin/env python3

import sys

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, GLib

from MainWindow import MainWindow


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="tr.org.pardus.xfce-greeter", flags=Gio.ApplicationFlags(8),
                         **kwargs)
        self.window = None

        self.add_main_option(
            "page",
            ord("p"),
            GLib.OptionFlags(0),
            GLib.OptionArg(1),
            "Details page of application",
            None,
        )

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(self)
        else:
            self.window.control_args()
            self.window.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()
        self.args = options
        self.activate()
        return 0


app = Application()
app.run(sys.argv)
