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
        self.size = (self.grid[0] + self.margin[0], self.grid[1] + self.margin[1])

        self.scale = 0.01
        self.zoom = 1

        self.origin = (0, 0)
        self.drag = (0, 0)

        self.linewidth = 1
        self.linecap = 1
        self.linejoin = 1

        self.connect('button-press-event', self.on_mouse_press)
        self.connect('motion-notify-event', self.on_mouse_move)
        self.connect('button-release-event', self.on_mouse_release)
        self.connect('scroll-event', self.on_scroll)
        self.connect('size-allocate', self.on_resize)
        self.connect('draw', self.draw)
        self.set_events(self.get_events() |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.SCROLL_MASK)

    def draw(self, widget, ctx):
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
        ctx.paint()

        ori = self.origin
        ctx.translate(ori[0] - (self.size[0] / 2 / self.scale * self.zoom),
                      ori[1] - (self.size[1] / 2 / self.scale * self.zoom))
        ctx.scale(1 / self.scale * self.zoom, 1 / self.scale * self.zoom)

        self.draw_grid(ctx)

        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(self.linewidth)
        ctx.set_line_cap(self.linecap)
        ctx.set_line_join(self.linejoin)

        ctx.new_path()
        if len(self.path) == 1:
            x, y = self.path[0]
            ctx.line_to(x + self.margin[0], y + self.margin[1])
            ctx.line_to(x + self.margin[0], y + self.margin[1])
        else:
            for x, y in self.path:
                ctx.line_to(x + self.margin[0], y + self.margin[1])

        ctx.stroke()

    def draw_grid(self, ctx):
        ctx.set_source_rgb(0.13, 0.3, 0.89)
        for x in range(self.grid[0]):
            for y in range(self.grid[1]):
                ctx.arc(x + self.margin[0],
                        y + self.margin[1],
                        self.scale * 5 / self.zoom,
                        0.0,
                        2 * pi)
                ctx.fill()

    def on_mouse_move(self, widget, event):
        if event.state & Gdk.EventMask.BUTTON_PRESS_MASK:
            self.add_point(event.x, event.y)
        if event.state & Gdk.ModifierType.BUTTON2_MASK:
            ori = self.origin
            prev = self.drag
            self.origin = (ori[0] + (event.x - prev[0]), ori[1] + (event.y - prev[1]))
            self.drag = (event.x, event.y)
            self.queue_draw()

    def on_mouse_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.add_point(event.x, event.y)
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.path = []
            self.queue_draw()
        elif event.button == Gdk.BUTTON_MIDDLE:
            self.drag = (event.x, event.y)

    def on_mouse_release(self, widget, event):
        if event.button == Gdk.BUTTON_MIDDLE:
            ori = self.origin
            prev = self.drag
            self.origin = (ori[0] + (event.x - prev[0]), ori[1] + (event.y - prev[1]))
            self.drag = (0, 0)
            self.queue_draw()

    def on_scroll(self, widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            self.zoom += 0.1
        else:
            self.zoom += -0.1
        if self.zoom < 0.1:
            self.zoom = 0.1
        self.queue_draw()

    def on_resize(self, widget, rect):
        self.origin = (rect.width / 2, rect.height / 2)
        self.scale = (self.grid[1] + self.margin[1]) / rect.height

    def add_point(self, x, y):
        ori = self.origin
        translate = (ori[0] - (self.size[0] / 2 / self.scale * self.zoom),
                     ori[1] - (self.size[1] / 2 / self.scale * self.zoom))
        point = (
            round((x-translate[0]) * self.scale / self.zoom)-self.margin[0],
            round((y-translate[1]) * self.scale / self.zoom)-self.margin[1]
        )

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
