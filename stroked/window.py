import gi
import importlib.resources

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from stroked.ui import Canvas


class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    def __init__(self, app):
        super().__init__(application=app, title='Stroked')
        self.set_size_request(-1, 700)


        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)

        with importlib.resources.path(
            'stroked.data.interface', 'menubar.glade'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        builder.connect_signals(self)
        box.add(builder.get_object("menubar"))

        hbox = Gtk.Box()
        box.pack_start(hbox, True, True, 0)

        canvas = Canvas()
        hbox.pack_start(canvas, True, True, 0)

        with importlib.resources.path(
            'stroked.data.interface', 'canvas_settings.glade'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        builder.connect_signals(canvas)

        canvas_settings = builder.get_object('canvas_settings')
        hbox.add(canvas_settings)

        self.show_all()
