import gi
import importlib.resources

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from stroked.ui import Canvas


class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    def __init__(self, app):
        super().__init__(application=app, title='Stroked')
        self.set_size_request(-1, 700)

        menu = self.build_main_menu(app)
        self.set_titlebar(menu)

        main_box = Gtk.VBox()
        self.add(main_box)

        hbox = Gtk.Box()
        main_box.pack_start(hbox, True, True, 0)

        paned = Gtk.Paned()
        hbox.pack_start(paned, True, True, 0)

        paned_box = Gtk.Box()
        paned.add(paned_box)

        self.notebook, self.glyph_set = self.build_notebook()
        paned_box.pack_start(self.notebook, True, True, 0)

        self.show_all()

    def build_main_menu(self, app):
        with importlib.resources.path(
            'stroked.data.interface', 'menubar.glade'
        ) as path:
            builder = Gtk.Builder.new_from_file(str(path))
        builder.connect_signals(app)

        return builder.get_object("menubar")

    def build_notebook(self):
        notebook = Gtk.Notebook()

        glyph_set_zone = Gtk.ScrolledWindow()
        notebook.append_page(glyph_set_zone, Gtk.Label('Glyph Set'))

        glyph_set = Gtk.FlowBox(
            valign=Gtk.Align(1),
            homogeneous=True,
            min_children_per_line=2,
            max_children_per_line=100,
            can_focus=False
        )
        glyph_set.set_selection_mode(Gtk.SelectionMode.NONE)
        glyph_set_zone.add(glyph_set)

        self.populate_glyph_set(glyph_set)

        return notebook, glyph_set

    def populate_glyph_set(self, glyph_set):
        glyphs = range(32, 127)

        for glyph in glyphs:
            child = Gtk.FlowBoxChild(can_focus=False)
            child.set_size_request(60, 75)
            button = Gtk.Button(label=chr(glyph))
            child.add(button)
            button.connect('button-press-event', self.on_glyph_click, glyph)
            child.set_events(child.get_events() | Gdk.EventMask.BUTTON_PRESS_MASK)
            glyph_set.add(child)

    def on_glyph_click(self, widget, event, n):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            canvas = Canvas()
            page_num = self.notebook.append_page(canvas, Gtk.Label(chr(n)))
            self.show_all()
            self.notebook.set_current_page(page_num)
