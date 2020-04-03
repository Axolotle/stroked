from gi.repository import Gtk, Gdk


@Gtk.Template.from_resource('/space/autre/stroked/ui/glyph_list.ui')
class GlyphList(Gtk.FlowBox):
    __gtype_name__ = 'GlyphList'

    def __init__(self):
        super().__init__()
        self.populate()

    @property
    def tabs(self):
        return self.get_toplevel().tabs

    @property
    def font(self):
        return self.get_toplevel().font

    def populate(self):
        glyphs = range(32, 127)

        for glyph in glyphs:
            child = Gtk.FlowBoxChild(can_focus=False)
            child.set_size_request(60, 75)
            button = Gtk.Button(label=chr(glyph))
            button.connect('button-press-event', self.on_glyph_click, glyph)
            child.add(button)
            self.add(child)
        self.show_all()

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_glyph_click(self, widget, event, n):
        font = self.font
        tabs = self.tabs
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            label = chr(n)
            glyph = font.newGlyph(label) if label not in font else font[label]
            tab_num = tabs.find_num_from_tab_label(label)
            if tab_num is None:
                tab_num = tabs.add_tab(label, glyph)
            tabs.set_current_page(tab_num)
