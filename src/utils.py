#!/usr/bin/env python3

import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def getenv(name):
    return os.environ.get(name, default="")


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


def change_lines_in_file(filepath, old_lines, new_lines):
    """
    Change lines in a file, whole line, not a word. Example usage:

    `change_lines_in_file("file.txt", ["old line 1", "old line 2"], ["new line 1", "new line 2"])`

    file.txt content:

    old line 1
    old line 2
    old line 3

    -- becomes:

    new line 1
    new line 2
    old line 3
    """
    content = ""
    with open(filepath, "r") as f:
        content = f.read()

    if not content:
        return

    with open(filepath, "w") as f:
        for line in content.splitlines():
            try:
                index = old_lines.index(line)
                new_line = new_lines[index]

                f.write(new_line + "\n")
                continue
            except ValueError as e:
                pass
            except IndexError as e:
                pass

            f.write(line + "\n")
