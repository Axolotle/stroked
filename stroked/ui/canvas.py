import cairo
import gi
from math import pi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Canvas(Gtk.DrawingArea):
    __gtype_name__ = 'Canvas'

    def __init__(self):
        super().__init__()
        self.path = []
        self.grid = (5, 9)
        self.margin = (1, 1)

        self.scale = None
        self.linewidth = 1
        self.linecap = 1
        self.linejoin = 1

        self.translation = {
            'origin': (1, 1),
            'start': (0, 0),
            'current': (0, 0)
        }

        self.connect('draw', self.draw)
        self.connect('button-press-event', self.on_mouse_press)
        self.connect('motion-notify-event', self.on_mouse_move)
        self.connect('button-release-event', self.on_mouse_release)
        self.connect('size-allocate', self.on_resize)
        self.set_events(self.get_events() |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK)

    def draw(self, widget, ctx):
        scale = 1 / self.scale

        ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
        ctx.paint()

        ori = self.translation['origin']
        start = self.translation['start']
        cur = self.translation['current']
        ctx.translate(ori[0] + (cur[0] - start[0]), ori[1] + (cur[1] - start[1]))
        ctx.scale(scale, scale)

        self.draw_grid(ctx)

        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(self.linewidth)
        ctx.set_line_cap(self.linecap)
        ctx.set_line_join(self.linejoin)

        ctx.new_path()
        if len(self.path) == 1:
            x, y = self.path[0]
            ctx.line_to(x, y)
            ctx.line_to(x, y)
        else:
            for x, y in self.path:
                ctx.line_to(x, y)
        ctx.stroke()

    def draw_grid(self, ctx):
        ctx.set_source_rgb(0.13, 0.3, 0.89)
        for x in range(self.grid[0]):
            for y in range(self.grid[1]):
                ctx.arc(x, y, self.scale * 5, 0.0, 2 * pi)
                ctx.fill()

    def on_mouse_move(self, widget, event):
        if event.state & Gdk.EventMask.BUTTON_PRESS_MASK:
            self.add_point(event.x, event.y)
        if event.state & Gdk.ModifierType.BUTTON2_MASK:
            self.translation['current'] = (event.x, event.y)
            self.queue_draw()

    def on_mouse_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.add_point(event.x, event.y)
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.path = []
            self.queue_draw()
        elif event.button == Gdk.BUTTON_MIDDLE:
            self.translation['start'] = (event.x, event.y)
            self.translation['current'] = (event.x, event.y)

    def on_mouse_release(self, widget, event):
        if event.button == Gdk.BUTTON_MIDDLE:
            ori = self.translation['origin']
            start = self.translation['start']
            cur = self.translation['current']
            self.translation['origin'] = (ori[0] + (cur[0] - start[0]), ori[1] + (cur[1] - start[1]))
            start = self.translation['start'] = (0, 0)
            cur = self.translation['current'] = (0, 0)
            self.queue_draw()

    def on_resize(self, widget, rect):
        self.scale = (self.grid[1] + self.margin[1]) / rect.height
        factor = 1 / self.scale
        self.translation['origin'] = (
            self.margin[0] * factor, self.margin[1] * factor
        )
        self.set_size_request((self.grid[0] + self.margin[0]) * factor, -1)

    def add_point(self, x, y):
        translate = self.translation['origin']
        point = (round((x-translate[0]) * self.scale), round((y-translate[1]) * self.scale))
        if len(self.path) == 0 or self.path[-1] != point:
            self.path.append(point)
            self.queue_draw()

    def on_property_changed(self, combo):
        property_name = combo.get_name()
        if property_name in ['linecap', 'linejoin']:
            property_value = combo.get_active()
            setattr(self, property_name, property_value)
            self.queue_draw()

    def on_linewidth_changed(self, elem):
        self.linewidth = round(elem.get_value(), 2)
        self.queue_draw()
