

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

    def on_key_press(self, canvas, event):
        pass

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self):
        pass

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, canvas, color=(0.13, 0.3, 0.89)):
        pass

    def draw_specific(self, ctx, canvas):
        pass
