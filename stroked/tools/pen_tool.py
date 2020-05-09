from gi.repository import Gdk

from .base_tool import BaseTool


class PenTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.is_drawing = False

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.add_point(canvas.glyph, canvas.mouse_pos)
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.stop_drawing(canvas)

    def on_mouse_move(self, canvas, event):
        if self.is_drawing:
            self.update_last_point(canvas.glyph, canvas.mouse_pos)

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self):
        self.is_drawing = False

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
