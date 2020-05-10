from gi.repository import Gtk, Gdk, GLib

from .base_tool import BaseTool
from .helpers import find_point_in_glyph


class SelectTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.selected = []
        self.drag_origin = (0, 0)

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.drag_origin = canvas.mouse_pos
            modifier = event.state & Gdk.ModifierType.SHIFT_MASK
            if event.type == Gdk.EventType.BUTTON_PRESS:
                self.on_right_click(canvas, canvas.mouse_pos, False, modifier)
            if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                self.on_right_click(canvas, canvas.mouse_pos, True, modifier)

    def on_mouse_move(self, canvas, event):
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            selection = canvas.glyph.selection
            dx, dy = self.drag_origin
            mx, my = canvas.mouse_pos
            translate = (mx - dx, my - dy)
            for point in selection:
                point.move(translate)
            self.drag_origin = (mx, my)

    def on_right_click(self, canvas, pos, double, modifier):
        glyph = canvas.glyph
        point, contour = find_point_in_glyph(glyph, pos)
        if point:
            selection = glyph.selection
            if double:
                contour.selected = True
                return
            if not modifier:
                glyph.selected = False
            point.selected = True if not modifier else not point.selected
        else:
            glyph.selected = False
        canvas.queue_draw()

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self, canvas):
        self.drag_origin = (0, 0)

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, canvas):
        pt, contour = find_point_in_glyph(canvas.glyph, canvas.mouse_pos)
        color = (1, 0, 106/255) if pt is not None else (0.13, 0.3, 0.89)
        super().draw_cursor(ctx, canvas, color=color)
