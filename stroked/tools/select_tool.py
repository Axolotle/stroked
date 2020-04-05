from gi.repository import Gdk

from .base_tool import BaseTool


class SelectTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.selected = []
        self.drag = (0, 0)

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        super().on_mouse_press(canvas, event)
        if event.button == Gdk.BUTTON_PRIMARY:
            pt = self.get_point_in_glyph(canvas.mouse_pos)
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
        super().on_mouse_move(canvas, event)
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            mouse_pos = canvas.mouse_pos

            if len(self.selected):
                for pt in self.selected:
                    if self.drag != mouse_pos:
                        pt.move((mouse_pos[0] - self.drag[0],
                                 mouse_pos[1] - self.drag[1]))
                self.drag = mouse_pos

    def on_mouse_release(self, canvas, event):
        super().on_mouse_release(canvas, event)
        if event.button == Gdk.BUTTON_PRIMARY:
            self.drag = (0, 0)

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self):
        self.selected = []
        self.drag = (0, 0)

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, mouse_pos):
        pt = self.get_point_in_glyph(mouse_pos)
        color = (1, 0, 106/255) if pt is not None else (0.13, 0.3, 0.89)
        super().draw_cursor(ctx, mouse_pos, color=color)
