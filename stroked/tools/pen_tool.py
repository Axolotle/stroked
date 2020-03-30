import gi

gi.require_version('Gtk', '3.0')
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
            pt = canvas.screen_to_point(event.x, event.y)
            self.add_point(canvas.glyph, pt)
            canvas.queue_draw()
        elif event.button == Gdk.BUTTON_SECONDARY:
             self.stop_drawing()
             canvas.queue_draw()
        else:
            super().on_mouse_press(canvas, event)
            return

    def on_mouse_move(self, canvas, event):
        if self.is_drawing:
            pt = canvas.screen_to_point(event.x, event.y)
            self.update_last_point(canvas.glyph, pt)
            canvas.queue_draw()
        super().on_mouse_move(canvas, event)

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self):
        if self.is_drawing:
            self.stop_drawing()

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

    def stop_drawing(self):
        contour = self.canvas.glyph[-1]
        contour.removePoint(contour[-1])
        self.is_drawing = False
