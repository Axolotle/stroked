from math import pi

from gi.repository import Gdk


class BaseTool():
    def __init__(self):
        super().__init__()
        self.canvas = None

    def set_canvas(self, canvas):
        self.reset()
        self.canvas = canvas

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_MIDDLE:
            canvas.drag = (event.x, event.y)
        canvas.queue_draw()

    def on_mouse_move(self, canvas, event):
        canvas.mouse_pos = canvas.screen_to_point(event.x, event.y)
        if event.state & Gdk.ModifierType.BUTTON2_MASK:
            ori = canvas.origin
            prev = canvas.drag
            canvas.origin = (ori[0] + (event.x - prev[0]),
                             ori[1] + (event.y - prev[1]))
            canvas.drag = (event.x, event.y)
        canvas.queue_draw()

    def on_mouse_release(self, canvas, event):
        if event.button == Gdk.BUTTON_MIDDLE:
            ori = canvas.origin
            prev = canvas.drag
            canvas.origin = (ori[0] + (event.x - prev[0]),
                             ori[1] + (event.y - prev[1]))
            canvas.drag = (0, 0)
        canvas.queue_draw()

    def on_scroll(self, canvas, event):
        if event.direction == Gdk.ScrollDirection.UP:
            canvas.zoom += 0.1
        else:
            canvas.zoom += -0.1
        if canvas.zoom < 0.1:
            canvas.zoom = 0.1
        canvas.queue_draw()

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self):
        pass

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, mouse_pos, color=(0.13, 0.3, 0.89)):
        scale, zoom = self.canvas.scale, self.canvas.zoom
        ctx.set_source_rgb(*color)
        ctx.set_line_width(scale * 2 / zoom)
        ctx.arc(mouse_pos[0], mouse_pos[1], scale * 6 / zoom, 0.0, 2 * pi)
        ctx.stroke()

    # ╭──────────────╮
    # │ TOOL HELPERS │
    # ╰──────────────╯

    def get_point_in_glyph(self, pt):
        for contour in self.canvas.glyph:
            for point in contour:
                if pt[0] == point.x and pt[1] == point.y:
                    return point
        return None

    def get_point_in_contour(self, contour, pt):
        for point in contour:
            if pt[0] == point.x and pt[1] == point.y:
                return point
        return None
