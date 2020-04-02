import gi
import importlib.resources

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import stroked.ui
import stroked.settings as stg
from defcon import Font


class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    def __init__(self, app, font, filename='Untitled', font_path=None):
        title = '{} - Stroked'.format(filename)
        super().__init__(application=app, title=title)
        self.set_size_request(-1, 700)

        menu = self.build_main_menu(app)
        self.set_titlebar(menu)

        with importlib.resources.path(
            'stroked.data.ui', 'window.ui'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        builder.connect_signals(self)

        main_box = builder.get_object('main-box')
        self.add(main_box)

        self.tabs = builder.get_object('tabs')

        self.toolbar = builder.get_object('toolbar')
        self.toolbar.connect('notify::current-tool', self.tabs.on_tool_changed)

        self.glyph_list = builder.get_object('glyph-list')
        self.populate_glyph_set(self.glyph_list)

        self.font = font
        self.filename = filename
        self.path = font_path
        self.font.addObserver(self, 'on_font_changed', 'Font.Changed')

        self.connect('key-press-event', self.on_keypress)
        self.connect('delete-event', self.on_close)

        self.show_all()

    def build_main_menu(self, app):
        with importlib.resources.path(
            'stroked.data.ui', 'menubar.ui'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        # builder.connect_signals(app)

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
            glyph = self.font.newGlyph(label) if label not in self.font else self.font[label]
            tab_num = self.tabs.find_num_from_tab_label(label)
            if tab_num is None:
                tab_num = self.tabs.add_tab(label, glyph)
            self.tabs.set_current_page(tab_num)

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

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_keypress(self, widget, event):
        if not event.state & Gdk.ModifierType.CONTROL_MASK:
            return
        key_name = Gdk.keyval_name(event.keyval)
        if key_name == 'w':
            self.tabs.close_tab()

    def on_close(self, window=None, event=None):
        stop_propagation = False
        if self.font.dirty:
            dialog = stroked.ui.dialogs.DialogSaveBeforeQuit(self)
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                saved = self.get_application().on_save()
                stop_propagation = not saved
            elif response == Gtk.ResponseType.NO:
                stop_propagation = False
            elif response == Gtk.ResponseType.CANCEL:
                stop_propagation = True

        return stop_propagation

    # ╭────────────────────────╮
    # │ DEFCON EVENTS HANDLERS │
    # ╰────────────────────────╯

    def on_font_changed(self, notification=None):
        title = self.get_title()
        dirty = '*' if self.font.dirty else ''
        supposed_title = '{}{} - Stroked'.format(dirty, self.filename)
        if title != supposed_title:
            self.set_title(supposed_title)
