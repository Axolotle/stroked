import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Canvas(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.path = []

        self.connect('draw', self.draw)
        self.connect('motion-notify-event', self.mouse_move)
        self.connect('button-press-event', self.mouse_press)
        self.connect('button-release-event', self.mouse_release)
        self.set_events(self.get_events() |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK)

    def draw(self, widget, ctx):
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.paint()

        ctx.set_source_rgba(255, 255, 255, 1)
        ctx.set_line_width(10)
        ctx.set_line_cap(cairo.LineCap.ROUND)
        ctx.set_line_join(cairo.LineJoin.ROUND)
        ctx.new_path()
        for x, y in self.path:
            ctx.line_to(x, y)
        ctx.stroke()

    def mouse_move(self, widget, event):
        if event.state & Gdk.EventMask.BUTTON_PRESS_MASK:
            self.path.append((event.x, event.y))
            widget.queue_draw()

    def mouse_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.path.append((event.x, event.y))
            widget.queue_draw()
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.path = []

    def mouse_release(self, widget, event):
        widget.queue_draw()
