import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from stroked.app import StrokedApp


app = StrokedApp()
Gtk.main()
