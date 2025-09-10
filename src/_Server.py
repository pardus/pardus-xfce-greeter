#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 14:53:00 2020

@author: fatih
"""

import gi
import json

gi.require_version("GLib", "2.0")
gi.require_version("Soup", "2.4")
from gi.repository import GLib, Gio


class Server(object):
    def __init__(self):
        pass

    def get(self, url):
        file = Gio.File.new_for_uri(url)
        file.load_contents_async(None, self._open_stream)

    def _open_stream(self, file, result):
        try:
            success, data, etag = file.load_contents_finish(result)
        except GLib.Error as error:
            self.error_message = error.message
            print("_open_stream Error: {}, {}".format(error.domain, error.message))

            # if error.matches(Gio.tls_error_quark(),  Gio.TlsError.BAD_CERTIFICATE):
            if error.domain == GLib.quark_to_string(Gio.tls_error_quark()):
                response = {"error": True, "tlserror": True, "message": error.message}
                self.ServerGet(response=response)  # Send to MainWindow
                return response

            response = {"error": True, "message": error.message}
            self.ServerGet(response=response)  # Send to MainWindow
            return response

        if success:
            self.ServerGet(json.loads(data))
        else:
            print("ServerGet is not success")
            self.ServerGet(response=None)  # Send to MainWindow
