import weakref

from gi.repository import Gtk


@Gtk.Template.from_resource('/space/autre/stroked/ui/glyph_list.ui')
class GlyphList(Gtk.FlowBox):
    __gtype_name__ = 'GlyphList'

    def __init__(self):
        super().__init__()
        self.connect('realize', self.display_glyphs)

    @property
    def tabs(self):
        return self.get_toplevel().tabs

    @property
    def font(self):
        return self.get_toplevel().font

    def display_glyphs(self, widget):
        glyph_names = self.font.glyphOrder
        for name in glyph_names:
            self.add(GlyphItem(name, self.font.active_master[name]))
        self.show_all()

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    @Gtk.Template.Callback('on_glyph_clicked')
    def _on_glyph_clicked(self, glyph_list, glyph_item):
        label_text = glyph_item.get_child().get_label()
        self.tabs.open_tab(label_text)


class GlyphItem(Gtk.FlowBoxChild):
    __gtype_name__ = 'GlyphItem'

    def __init__(self, label, glyph):
        super().__init__()
        self.set_size_request(60, 75)
        self.add(Gtk.Label(label=label))
        self._glyph = weakref.ref(glyph)
        glyph.addObserver(self, 'on_glyph_name_changed', 'Glyph.NameChanged')

    @property
    def glyph(self):
        return self._glyph()

    def on_glyph_name_changed(self, notification):
        old_name, new_name = notification.data.values()
        self.get_child().set_label(new_name)
        self.get_parent().tabs.rename_tab(old_name, new_name)
