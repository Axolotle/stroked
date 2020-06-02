from gi.repository import Gtk


@Gtk.Template.from_resource('/space/autre/stroked/ui/panels.ui')
class GlyphInfos(Gtk.Grid):
    __gtype_name__ = 'GlyphInfos'

    entry_name = Gtk.Template.Child('glyph-name-entry')
    entry_unicodes = Gtk.Template.Child('glyph-unicodes-entry')
    entry_width = Gtk.Template.Child('glyph-width-entry')
    entry_leftMargin = Gtk.Template.Child('glyph-left-entry')
    entry_rightMargin = Gtk.Template.Child('glyph-right-entry')

    def __init__(self):
        super().__init__()
        self._glyph = None

    def do_realize(self):
        Gtk.Grid.do_realize(self)
        for attr in self.__gtktemplate_widgets__.values():
            widget = getattr(self, attr)
            widget.connect(
                'safe_value_changed', self.on_value_changed, attr.split('_')[-1]
            )

    def on_value_changed(self, entry, value, attr):
        if self._glyph is not None:
            setattr(self._glyph, attr, value)

    def update_attributes(self, glyph):
        for attr in ('name', 'unicodes', 'width', 'leftMargin', 'rightMargin'):
            getattr(self, 'entry_' + attr).set_value(getattr(glyph, attr))

    def on_glyph_changed(self, notification):
        glyph = self._glyph
        self.entry_width.set_value(glyph.width)
        self.entry_leftMargin.set_value(glyph.leftMargin)
        self.entry_rightMargin.set_value(glyph.rightMargin)

    def _unsubscribe_to_glyph(self):
        if self._glyph is None:
            return
        glyph = self._glyph
        glyph.removeObserver(self, 'Glyph.Changed')

    def _subscribe_to_glyph(self, glyph):
        glyph.addObserver(self, 'on_glyph_changed', 'Glyph.Changed')

    def set_current_glyph(self, glyph):
        self._unsubscribe_to_glyph()
        self._glyph = glyph
        self.update_attributes(glyph)
        self._subscribe_to_glyph(glyph)
