import gi

gi.require_version("GLib", "2.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GLib, GdkPixbuf, Gio


class Stream(object):
    def __init__(self):
        pass

    def fetch(self, data):
        img_file = Gio.File.new_for_uri(data["icon"])
        img_file.read_async(GLib.PRIORITY_LOW, None, self._open_stream, data)

    def _open_stream(self, img_file, result, data):
        try:
            stream = img_file.read_finish(result)
        except GLib.Error as error:
            print("_open_stream Error: {}, {}".format(error.domain, error.message))
            return False

        GdkPixbuf.Pixbuf.new_from_stream_async(stream, None, self._pixbuf_loaded, data)

    def _pixbuf_loaded(self, stream, result, data):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream_finish(result)
        except GLib.Error as error:
            print("_pixbuf_loaded Error: {}, {}".format(error.domain, error.message))
            return False

        stream.close_async(GLib.PRIORITY_LOW, None, self._close_stream, None)
        self.StreamGet(pixbuf, data)

    def _close_stream(self, stream, result, data):
        try:
            stream.close_finish(result)
        except GLib.Error as error:
            print("Error: {}, {}".format(error.domain, error.message))
