import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


grid = (6, 10)

class Canvas(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.path = []

        self.scale = None

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

        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(1)
        ctx.set_line_cap(cairo.LineCap.ROUND)
        ctx.set_line_join(cairo.LineJoin.ROUND)
        ctx.scale(scale, scale)
        ctx.new_path()
        if len(self.path) == 1:
            x, y = self.path[0]
            ctx.line_to(x, y)
            ctx.line_to(x, y)
        else:
            for x, y in self.path:
                ctx.line_to(x, y)
        ctx.stroke()

    def on_mouse_move(self, widget, event):
        if event.state & Gdk.EventMask.BUTTON_PRESS_MASK:
            self.add_point(event.x, event.y)

    def on_mouse_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.add_point(event.x, event.y)
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.path = []

    def on_mouse_release(self, widget, event):
        self.queue_draw()

    def on_resize(self, widget, rect):
        self.scale = grid[1] / rect.height

    def add_point(self, x, y):
        point = (round(x * self.scale), round(y * self.scale))
        if len(self.path) == 0 or self.path[-1] != point:
            self.path.append(point)
            self.queue_draw()
