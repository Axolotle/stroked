import cairo
import gi
from math import pi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Canvas(Gtk.DrawingArea):
    __gtype_name__ = 'Canvas'

    def __init__(self):
        super().__init__()
        self.grid = (5, 9)
        self.margin = (1, 1)
        self.size = (self.grid[0] + self.margin[0], self.grid[1] + self.margin[1])

        self.guides = {
            'ascender': 2,
            'baseline': 7,
            'descender': 9
        }

        self.paths = []
        self.path_index = None

        self.scale = 0.01
        self.zoom = 1

        self.origin = (0, 0)
        self.drag = (0, 0)

        self.linewidth = 1
        self.linecap = 1
        self.linejoin = 1

        self.hover = None
        self.drawing = False
        self.next_point = None

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

        self.draw_guides(ctx)
        self.draw_grid(ctx)

        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(self.linewidth)
        ctx.set_line_cap(self.linecap)
        ctx.set_line_join(self.linejoin)

        for path in self.paths:
            ctx.new_path()
            for x, y in path:
                ctx.line_to(x + self.margin[0], y + self.margin[1])
            ctx.stroke()
        # print(self.paths)
        if self.drawing:
            ctx.new_path()
            for pt in [self.paths[self.path_index][-1], self.next_point]:
                ctx.line_to(pt[0] + self.margin[0], pt[1] + self.margin[1])
            ctx.stroke()

        if self.hover is not None:
            self.draw_selector(ctx)

    def draw_grid(self, ctx):
        ctx.set_source_rgb(0.13, 0.3, 0.89)
        for x in range(self.grid[0]):
            for y in range(self.grid[1]):
                ctx.arc(x + self.margin[0],
                        y + self.margin[1],
                        self.scale * 2 / self.zoom,
                        0.0,
                        2 * pi)
                ctx.fill()

    def draw_guides(self, ctx):
        ctx.set_source_rgb(1, 0, 106/255)
        ctx.set_line_width(self.scale / self.zoom)
        for y in self.guides.values():
            ctx.move_to(-1, y + 0.5)
            ctx.line_to(self.size[0] + 1, y + 0.5)
        ctx.stroke()

    def draw_selector(self, ctx):
        color = (1, 0, 106/255) if self.hover['in_path'] else (0.13, 0.3, 0.89)
        ctx.set_source_rgb(*color)
        ctx.set_line_width(self.scale * 2 / self.zoom)
        x, y = self.hover['point']
        ctx.arc(x + self.margin[0],
                y + self.margin[1],
                self.scale * 6 / self.zoom,
                0.0,
                2 * pi)
        ctx.stroke()
        if self.hover['in_path']:
            ctx.new_path()
            ctx.arc(x + self.margin[0],
                    y + self.margin[1],
                    self.scale * 2 / self.zoom,
                    0.0,
                    2 * pi)
            ctx.fill()

    def on_mouse_move(self, widget, event):
        if event.state & Gdk.ModifierType.BUTTON2_MASK:
            ori = self.origin
            prev = self.drag
            self.origin = (ori[0] + (event.x - prev[0]), ori[1] + (event.y - prev[1]))
            self.drag = (event.x, event.y)
            self.queue_draw()
        else:
            pt = self.screen_to_point(event.x, event.y)
            self.on_hover(pt)
            self.next_point = pt

    def on_mouse_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.drawing = True
            if self.path_index is None:
                self.paths.append([])
                self.path_index = len(self.paths) - 1
            pt = self.screen_to_point(event.x, event.y)
            self.add_point(pt)
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.drawing = False
            self.path_index = None
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

    def screen_to_point(self, x, y):
        ori = self.origin
        translate = (ori[0] - (self.size[0] / 2 / self.scale * self.zoom),
                     ori[1] - (self.size[1] / 2 / self.scale * self.zoom))
        return (
            round((x-translate[0]) * self.scale / self.zoom) - self.margin[0],
            round((y-translate[1]) * self.scale / self.zoom) - self.margin[1]
        )

    def on_hover(self, pt):
        self.hover = {
            'point': pt,
            'in_path': True if self.path_index is not None \
                       and pt in self.paths[self.path_index] else False
        }
        self.queue_draw()

    def add_point(self, pt):
        path = self.paths[self.path_index]
        if len(path) == 0 or path[-1] != pt:
            path.append(pt)
            self.hover = {'point': pt, 'in_path': True}
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
