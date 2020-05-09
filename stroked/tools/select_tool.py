from gi.repository import Gdk

from .base_tool import BaseTool
from .helpers import get_point_in_glyph


class SelectTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.selected = []
        self.drag = (0, 0)

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            pt = get_point_in_glyph(canvas.glyph, canvas.mouse_pos)
            if pt is not None:
                if event.state & Gdk.ModifierType.SHIFT_MASK:
                    if pt in self.selected:
                        self.selected.pop(self.selected.index(pt))
                    else:
                        self.selected.append(pt)
                else:
                    self.selected = [pt]
                self.drag = canvas.mouse_pos
            else:
                self.selected = []

    def on_mouse_move(self, canvas, event):
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            if len(self.selected) and self.drag != canvas.mouse_pos:
                mx, my = canvas.mouse_pos
                dx, dy = self.drag
                translate = (mx - dx, my - dy)
                for pt in self.selected:
                    pt.move(translate)
                self.drag = canvas.mouse_pos

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self, canvas):
        self.selected = []
        self.drag = (0, 0)

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, canvas):
        pt = get_point_in_glyph(canvas.glyph, canvas.mouse_pos)
        color = (1, 0, 106/255) if pt is not None else (0.13, 0.3, 0.89)
        super().draw_cursor(ctx, canvas, color=color)
