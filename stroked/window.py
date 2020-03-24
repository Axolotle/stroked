import gi
import importlib.resources

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from stroked.ui import Tabs
import stroked.settings as stg


class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    def __init__(self, app):
        super().__init__(application=app, title='Stroked')
        self.set_size_request(-1, 700)

        menu = self.build_main_menu(app)
        self.set_titlebar(menu)

        with importlib.resources.path(
            'stroked.data.interface', 'window.glade'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        builder.connect_signals(self)

        main_box = builder.get_object('main-box')
        self.add(main_box)

        self.tabs = builder.get_object('tabs')
        self.glyph_list = builder.get_object('glyph-list')
        self.populate_glyph_set(self.glyph_list)

        self.connect('key-press-event', self.on_keypress)
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
            label = chr(n)
            tab_num = self.tabs.find_num_from_tab_label(label)
            if tab_num is None:
                tab_num = self.tabs.add_tab(label)
            self.tabs.set_current_page(tab_num)

    def on_keypress(self, widget, event):
        if not event.state & Gdk.ModifierType.CONTROL_MASK:
            return
        key_name = Gdk.keyval_name(event.keyval)
        if key_name == 'w':
            self.tabs.close_tab()

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

        stg.set(['linestyle', property_name], property_value)
        self.tabs.update_tab_draw()
