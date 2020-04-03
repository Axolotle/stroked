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
        for glyph in range(32, 127):
            self.add(GlyphItem(chr(glyph)))
        self.show_all()

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    @Gtk.Template.Callback('on_glyph_clicked')
    def _on_glyph_clicked(self, glyph_list, glyph_item):
        font = self.font
        tabs = self.tabs
        label = glyph_item.get_child().get_label()
        glyph = font.newGlyph(label) if label not in font else font[label]
        tab_num = tabs.find_num_from_tab_label(label)
        if tab_num is None:
            tab_num = tabs.add_tab(label, glyph)
        tabs.set_current_page(tab_num)


class GlyphItem(Gtk.FlowBoxChild):
    __gtype_name__ = 'GlyphItem'

    def __init__(self, label):
        super().__init__()
        self.set_size_request(60, 75)
        self.add(Gtk.Label(label=label))
