from gi.repository import Gdk
from math import pi

from .base_tool import BaseTool
from .helpers import round_point


class PenTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.is_drawing = False

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.add_point(canvas.glyph, round_point(canvas.mouse_pos))
        elif event.button == Gdk.BUTTON_SECONDARY:
            if self.is_drawing:
                self.stop_drawing(canvas)

    def on_mouse_move(self, canvas, event):
        pos = round_point(canvas.mouse_pos)
        if self.is_drawing:
            self.update_last_point(canvas.glyph, pos)

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self, canvas):
        if self.is_drawing:
            self.stop_drawing(canvas)

    def add_point(self, glyph, pt):
        if not self.is_drawing:
            contour = glyph.instantiateContour()
            glyph.appendContour(contour)
            contour.addPoint(pt, 'move')
            self.is_drawing = True
        else:
            contour = glyph[-1]
            contour[-1].x, contour[-1].y = pt
        contour.addPoint(pt, 'line')

    def update_last_point(self, glyph, pt):
        point = glyph[-1][-1]
        point.x, point.y = pt

    def stop_drawing(self, canvas):
        contour = canvas.glyph[-1]
        contour.removePoint(contour[-1])
        self.is_drawing = False

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, canvas, color=(0.13, 0.3, 0.89)):
        x, y = round_point(canvas.mouse_pos)
        scale = canvas.scale
        ctx.set_source_rgb(*color)
        ctx.set_line_width(2 / scale)
        ctx.arc(x, y, 10 / scale, 0.0, 2 * pi)
        ctx.stroke()
