import cairo
import gi
from math import pi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import stroked.settings as stg


class Canvas(Gtk.DrawingArea):
    __gtype_name__ = 'Canvas'

    def __init__(self):
        super().__init__()

        self.paths = []
        self.path_index = None

        self.scale = 0.01
        self.zoom = 1

        self.origin = (0, 0)
        self.drag = (0, 0)

        self.hover = None
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

    @property
    def grid_size(self):
        grid = stg.get('grid')
        return (grid['size'][0] + grid['margin'][0],
                grid['size'][1] + grid['margin'][1])

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

        for i, path in enumerate(self.paths):
            ctx.new_path()
            for x, y in path:
                ctx.line_to(x + margin[0], y + margin[1])
            if self.path_index == i and self.next_point is not None:
                x, y = self.next_point
                ctx.line_to(x + margin[0], y + margin[1])
            ctx.stroke()

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

    def add_point(self, pt):
        path = self.paths[self.path_index]
        if len(path) == 0 or path[-1] != pt:
            path.append(pt)
            self.hover = {'point': pt, 'in_path': True}
            self.queue_draw()
        elif path[-1] == pt and len(path) == 1:
            path.append(pt)
            self.stop_drawing()

    def stop_drawing(self):
        self.path_index = None
        self.next_point = None
        self.queue_draw()

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
            if self.path_index is None:
                self.paths.append([])
                self.path_index = len(self.paths) - 1
            pt = self.screen_to_point(event.x, event.y)
            self.add_point(pt)
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.stop_drawing()
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
