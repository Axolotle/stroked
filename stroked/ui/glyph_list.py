import weakref

from gi.repository import Gtk
import cairo

from stroked.pens import CairoStrokePen


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
        master = self.font.active_master
        for name in glyph_names:
            self.add(GlyphItem(name, master[name]))
        self.show_all()

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    @Gtk.Template.Callback('on_glyph_clicked')
    def _on_glyph_clicked(self, glyph_list, glyph_item):
        label_text = glyph_item.label.get_label()
        self.tabs.open_tab(label_text)


@Gtk.Template.from_resource('/space/autre/stroked/ui/glyph_item.ui')
class GlyphItem(Gtk.FlowBoxChild):
    __gtype_name__ = 'GlyphItem'

    label = Gtk.Template.Child('label')
    canvas = Gtk.Template.Child('canvas')

    def __init__(self, label, glyph):
        super().__init__()
        self.set_size_request(90, 120)
        self.label.set_label(label)
        self._glyph = weakref.ref(glyph)
        glyph.addObserver(self, '_on_glyph_name_changed', 'Glyph.NameChanged')

    @property
    def glyph(self):
        return self._glyph()

    def draw_glyph(self, ctx, glyph):
        layer_lib = self.glyph.layer.lib['space.autre.stroked']
        canvas_width, canvas_height = self.canvas_size
        glyph_height = layer_lib['ascender'] + abs(layer_lib['descender']) + 4
        scale = canvas_height / glyph_height
        ctx.translate((canvas_width - glyph.width * scale) / 2, 0)
        ctx.scale(scale, scale)
        ctx.translate(0.5, 2.5)
        ctx.set_line_width(0.1)
        glyph.draw(CairoStrokePen(ctx))

    def draw_placeholder(self, ctx, char):
        ctx.save()
        ctx.select_font_face(
            'Fira Mono', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        canvas_width, canvas_height = self.canvas_size
        margin = canvas_height / 10
        # font_extents() return a tuple with:
        # (ascent, descent, height, max_x_advance, max_y_advance)
        _, font_descent, font_height, _, _ = ctx.font_extents()
        # text_extents() return a tuple with:
        # (x_bearing, y_bearing, width, height, x_advance, y_advance)
        glyph_x_bearing, _, glyph_width, _, _, _ = ctx.text_extents(char)
        scale = (canvas_height - margin * 2) / (font_height + font_descent)
        ctx.translate(canvas_width / 2, canvas_height / 2)
        ctx.scale(scale, scale)
        ctx.translate(0, font_descent / 2)
        x = -glyph_x_bearing - glyph_width / 2
        y = -font_descent + font_height / 2
        ctx.move_to(x, y)
        ctx.set_source_rgba(1, 1, 1, 0.75)
        ctx.show_text(char)
        ctx.restore()

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    @Gtk.Template.Callback('on_canvas_resize')
    def _on_resize(self, widget, rect):
        self.canvas_size = (rect.width, rect.height)

    @Gtk.Template.Callback('on_canvas_draw')
    def _on_canvas_draw(self, canvas, ctx):
        glyph = self.glyph
        character = chr(glyph.unicodes[0])
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.paint()

        if len(glyph):
            self.draw_glyph(ctx, glyph)
        else:
            self.draw_placeholder(ctx, character)

    # ╭────────────────────────╮
    # │ DEFCON EVENTS HANDLERS │
    # ╰────────────────────────╯

    def _on_glyph_name_changed(self, notification):
        old_name, new_name = notification.data.values()
        self.get_child().set_label(new_name)
        self.get_parent().tabs.rename_tab(old_name, new_name)
