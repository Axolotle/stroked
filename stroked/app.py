import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class StrokedApp(Gtk.Window):
    def __init__(self, width=400, height=400):
        super().__init__(title='Stroked')
        self.set_default_size(width, height)

        box = Gtk.Box(spacing=6)
        self.add(box)

        self.connect('destroy', self.close)

        self.show_all()

    def close(self, window):
        Gtk.main_quit()
