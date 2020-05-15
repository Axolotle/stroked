import weakref
from math import pi

from gi.repository import Gtk, Gdk
import cairo

import stroked.settings as stg
from stroked.pens import CairoPen


class Canvas(Gtk.DrawingArea):
    __gtype_name__ = 'Canvas'

    def __init__(self):
        super().__init__()

        self._glyph = None
        self._tool = None

        self.scale = 1.0
        self.size = (0, 0)
        self.offset = (0, 0)
        self.drag_origin = (0, 0)
        # position of the mouse in pt
        self.mouse_pos = (0, 0)

        self.connect('button-press-event', self.on_mouse_press)
        self.connect('motion-notify-event', self.on_mouse_move)
        self.connect('button-release-event', self.on_mouse_release)
        self.connect('scroll-event', self.on_scroll)
        self.connect('enter-notify-event', self.on_cursor_changed)
        self.connect('leave-notify-event', self.on_cursor_changed)

        self.connect('size-allocate', self.on_resize)
        self.connect('draw', self.draw)
        self.set_events(
            self.get_events()
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.SCROLL_MASK
            | Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK)

    @property
    def glyph(self):
        if self._glyph is not None:
            return self._glyph()
        return None

    @glyph.setter
    def glyph(self, glyph):
        self._glyph = weakref.ref(glyph)
        self.queue_draw()

    def draw(self, widget, ctx):
        glyph = self.glyph
        layer_lib = self.glyph.layer.lib['space.autre.stroked']
        font = glyph.font

        grid = font.grid

        glyph_origin = grid[1] + layer_lib['descender']
        guides_x = (-0.5, grid[0] - 0.5)
        guides_y = [
            glyph_origin - pos - 0.5 for pos in [
                layer_lib['ascender'], layer_lib['capHeight'],
                layer_lib['xHeight'], 0, layer_lib['descender']
            ]
        ]
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.paint()
        # translate the grid zone in the canvas
        ctx.translate(*self.offset)
        # set the pt to px scale to draw directly with pt values
        ctx.scale(self.scale, self.scale)

        self.draw_guides(ctx, guides_x, guides_y)
        self.draw_grid(ctx, grid)

        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        linestyle = stg.get('linestyle')
        ctx.set_line_width(linestyle['linewidth'])
        ctx.set_line_cap(linestyle['linecap'])
        ctx.set_line_join(linestyle['linejoin'])

        # avoid linejoin and linecap problems
        ctx.set_tolerance(1)
        glyph.draw(CairoPen(ctx))

        ctx.set_tolerance(0.1)
        self.draw_points(ctx, glyph)

        if self.mouse_pos:
            self._tool.draw_cursor(ctx, self)
        self._tool.draw_specific(ctx, self)

    def draw_grid(self, ctx, size):
        ctx.set_source_rgb(0.13, 0.3, 0.89)
        for x in range(size[0]):
            for y in range(size[1]):
                ctx.arc(x, y, 2 / self.scale, 0.0, 2 * pi)
                ctx.fill()

    def draw_guides(self, ctx, guides_x, guides_y):
        ctx.set_source_rgb(1, 0, 106/255)
        ctx.set_line_width(1 / self.scale)  # 1px
        for y in guides_y:
            ctx.move_to(guides_x[0], y)
            ctx.line_to(guides_x[1], y)
            ctx.stroke()

    def draw_points(self, ctx, glyph):
        selection = glyph.selection
        r = 2 / self.scale
        r_selected = 5 / self.scale
        pi2 = 2 * pi
        for contour in glyph:
            ctx.set_source_rgb(0, 0, 0)
            for point in contour:
                if point in selection:
                    continue
                ctx.arc(point.x, point.y, r, 0.0, pi2)
                ctx.fill()
        ctx.set_source_rgb(1, 0, 106/255)
        for point in selection:
            ctx.arc(point.x, point.y, r_selected, 0.0, pi2)
            ctx.fill()

    # ╭─────────────────────╮
    # │ COORDINATES HELPERS │
    # ╰─────────────────────╯

    def pixel_to_point(self, x, y):
        offx, offy = self.offset
        scale = self.scale

        return ((x - offx) / scale,
                (y - offy) / scale)

    def update_drag_translation(self, x, y):
        dox, doy = self.drag_origin
        dx, dy = x - dox, y - doy

        offx, offy = self.offset
        self.offset = (offx + dx, offy + dy)

    def fit_grid_to_screen(self):
        size = self.get_allocated_size()[0]
        w, h = (size.width, size.height)
        grid_w, grid_h = self.glyph.font.grid

        scale = h / (grid_h + 1)
        grid_w, grid_h = ((grid_w - 1) * scale, (grid_h - 1) * scale)

        self.offset = ((w - grid_w) * 0.5, (h - grid_h) * 0.5)
        self.scale = scale
        self.size = (w, h)

    # ╭───────────────────────────╮
    # │ GTK INPUT EVENTS HANDLERS │
    # ╰───────────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_MIDDLE:
            self.drag_origin = (event.x, event.y)
        self._tool.on_mouse_press(self, event)
        self.queue_draw()

    def on_mouse_move(self, canvas, event):
        self.mouse_pos = self.pixel_to_point(event.x, event.y)
        if event.state & Gdk.ModifierType.BUTTON2_MASK:
            self.update_drag_translation(event.x, event.y)
            self.drag_origin = (event.x, event.y)
        self._tool.on_mouse_move(self, event)
        self.queue_draw()

    def on_mouse_release(self, canvas, event):
        if event.button == Gdk.BUTTON_MIDDLE:
            self.update_drag_translation(event.x, event.y)
            canvas.drag_origin = (0, 0)
            canvas.queue_draw()
        self._tool.on_mouse_release(self, event)
        self.queue_draw()

    def on_scroll(self, canvas, event):
        prev_scale = self.scale

        if event.direction == Gdk.ScrollDirection.UP:
            self.scale *= 1.1
        else:
            self.scale *= pow(1.1, -1)
        if canvas.scale <= 0:
            self.scale = 0.01

        offx, offy = self.offset
        diff = self.scale - prev_scale

        dx = (event.x - offx) / prev_scale * diff
        dy = (event.y - offy) / prev_scale * diff

        self.offset = (offx - dx, offy - dy)

        canvas.queue_draw()

    def on_resize(self, widget, rect):
        if self.size == (0, 0):
            self.fit_grid_to_screen()
            return

        old_w, old_h = self.size
        w, h = (rect.width, rect.height)
        offx, offy = self.offset

        dx, dy = (0.5 * (old_w - w), 0.5 * (old_h - h))

        self.offset = (offx - dx, offy - dy)
        self.size = (w, h)

    # ╭───────────────────────────╮
    # │ GTK OTHER EVENTS HANDLERS │
    # ╰───────────────────────────╯

    def on_cursor_changed(self, canvas, event):
        if event.type == Gdk.EventType.ENTER_NOTIFY:
            name = 'crosshair'
        else:
            name = 'default'
        cursor = Gdk.Cursor.new_from_name(Gdk.Display.get_default(), name)
        self.get_window().set_cursor(cursor)
