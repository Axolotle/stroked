import gi
import importlib.resources

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk, GObject

from stroked.ui import Canvas


class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    def __init__(self, app):
        super().__init__(application=app, title='Stroked')
        self.set_size_request(-1, 700)

        self.settings = {
            'linecap': 1,
            'linejoin': 1,
            'linewidth': 1
        }

        menu = self.build_main_menu(app)
        self.set_titlebar(menu)

        with importlib.resources.path(
            'stroked.data.interface', 'window.glade'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        builder.connect_signals(self)

        main_box = builder.get_object('main-box')
        self.add(main_box)

        self.notebook = builder.get_object('notebook')
        self.glyph_list = builder.get_object('glyph-list')
        self.populate_glyph_set(self.glyph_list)

        self.show_all()

    def build_main_menu(self, app):
        with importlib.resources.path(
            'stroked.data.interface', 'menubar.glade'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        builder.connect_signals(app)

        return builder.get_object("menubar")

    def populate_glyph_set(self, glyph_set):
        glyphs = range(32, 127)

        for glyph in glyphs:
            child = Gtk.FlowBoxChild(can_focus=False)
            child.set_size_request(60, 75)
            button = Gtk.Button(label=chr(glyph))
            button.connect('button-press-event', self.on_glyph_click, glyph)
            child.add(button)
            glyph_set.add(child)

    def on_glyph_click(self, widget, event, n):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            canvas = Canvas()
            page_num = self.notebook.append_page(canvas, Gtk.Label(chr(n)))
            self.show_all()
            self.notebook.set_current_page(page_num)

    def on_tab_changed(self, notebook, canvas, num):
        if num > 0:
            canvas.update_style(self.settings)

    def on_linestyle_changed(self, elem):
        property_name = None
        property_value = None
        if isinstance(elem, Gtk.ComboBox):
            property_name = elem.get_name()
            if property_name in ['linecap', 'linejoin']:
                property_value = elem.get_active()
        elif isinstance(elem, Gtk.SpinButton):
            property_name = elem.get_name()
            property_value = elem.get_value()

        self.settings[property_name] = property_value

        active_num = self.notebook.get_current_page()
        if active_num > 0:
            canvas = self.notebook.get_nth_page(active_num)
            setattr(canvas, property_name, property_value)
            canvas.queue_draw()
