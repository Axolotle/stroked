from math import pi

from gi.repository import Gdk


class BaseTool():

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        pass

    def on_mouse_move(self, canvas, event):
        pass

    def on_mouse_release(self, canvas, event):
        pass

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self, canvas):
        pass

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, canvas, color=(0.13, 0.3, 0.89)):
        mx, my = canvas.mouse_pos
        scale = canvas.scale
        ctx.set_source_rgb(*color)
        ctx.set_line_width(2 / scale)
        ctx.arc(mx, my, 10 / scale, 0.0, 2 * pi)
        ctx.stroke()
