import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo
from math import pi

import stroked.settings as stg
from stroked.pens import CairoPen


class Canvas(Gtk.DrawingArea):
    __gtype_name__ = 'Canvas'

    def __init__(self, glyph):
        super().__init__()
        # self._tool = None
        self.glyph = glyph

        self.scale = 0.01
        self.zoom = 1

        self.origin = (0, 0)
        self.drag = (0, 0)

        self.hover = None

        self.connect('button-press-event',
            lambda w, e: self._tool.on_mouse_press(w, e))
        self.connect('motion-notify-event',
            lambda w, e: self._tool.on_mouse_move(w, e))
        self.connect('button-release-event',
            lambda w, e: self._tool.on_mouse_release(w, e))
        self.connect('scroll-event',
            lambda w, e: self._tool.on_scroll(w, e))

        self.connect('size-allocate', self.on_resize)
        self.connect('draw', self.draw)
        self.set_events(self.get_events() |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.SCROLL_MASK)

    @property
    def _tool(self):
        return self.get_parent().current_tool

    def update_style(self, styles):
        for style_name, style_value in styles.items():
            setattr(self, style_name, style_value)

    def draw(self, widget, ctx):
        grid = stg.get('grid')
        size = grid['size']
        margin = grid['margin']
        full_size = (size[0] + margin[0], size[1] + margin[1])

        ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
        ctx.paint()

        ori = self.origin
        ctx.translate(ori[0] - (full_size[0] / 2 / self.scale * self.zoom),
                      ori[1] - (full_size[1] / 2 / self.scale * self.zoom))
        ctx.scale(1 / self.scale * self.zoom, 1 / self.scale * self.zoom)

        self.draw_guides(ctx, full_size)
        self.draw_grid(ctx, size, margin)

        ctx.set_source_rgba(1, 1, 1, 1)
        linestyle = stg.get('linestyle')
        ctx.set_line_width(linestyle['linewidth'])
        ctx.set_line_cap(linestyle['linecap'])
        ctx.set_line_join(linestyle['linejoin'])

        ctx.translate(margin[0], margin[1])
        self.glyph.draw(CairoPen(ctx))

        if self.hover is not None:
            self.draw_selector(ctx, margin)

    def draw_grid(self, ctx, size, margin):
        ctx.set_source_rgb(0.13, 0.3, 0.89)
        for x in range(size[0]):
            for y in range(size[1]):
                ctx.arc(x + margin[0],
                        y + margin[1],
                        self.scale * 2 / self.zoom,
                        0.0,
                        2 * pi)
                ctx.fill()

    def draw_guides(self, ctx, size):
        ctx.set_source_rgb(1, 0, 106/255)
        ctx.set_line_width(self.scale / self.zoom)
        for y in stg.get('guides').values():
            ctx.move_to(-1, y + 0.5)
            ctx.line_to(size[0] + 1, y + 0.5)
        ctx.stroke()

    def draw_selector(self, ctx, margin):
        color = (1, 0, 106/255) if self.hover['in_path'] else (0.13, 0.3, 0.89)
        ctx.set_source_rgb(*color)
        ctx.set_line_width(self.scale * 2 / self.zoom)
        x, y = self.hover['point']
        ctx.arc(x + margin[0],
                y + margin[1],
                self.scale * 6 / self.zoom,
                0.0,
                2 * pi)
        ctx.stroke()
        if self.hover['in_path']:
            ctx.new_path()
            ctx.arc(x + margin[0],
                    y + margin[1],
                    self.scale * 2 / self.zoom,
                    0.0,
                    2 * pi)
            ctx.fill()

    def screen_to_point(self, x, y):
        grid = stg.get('grid')
        margin = grid['margin']
        full_size = (grid['size'][0] + margin[0], grid['size'][1] + margin[1])
        ori = self.origin
        translate = (ori[0] - (full_size[0] / 2 / self.scale * self.zoom),
                     ori[1] - (full_size[1] / 2 / self.scale * self.zoom))
        return (
            round((x-translate[0]) * self.scale / self.zoom) - margin[0],
            round((y-translate[1]) * self.scale / self.zoom) - margin[1]
        )

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_resize(self, widget, rect):
        self.origin = (rect.width / 2, rect.height / 2)
        grid = stg.get('grid')
        self.scale = (grid['size'][1] + grid['margin'][0]) / rect.height

    def on_hover(self, pt):
        self.hover = {
            'point': pt,
            'in_path': any(pt in path for path in self.paths)
        }
        self.queue_draw()

    def on_delete(self):
        self.paths = []
        self.stop_drawing()
