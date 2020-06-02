from gi.repository import Gdk
from math import pi

from .base_tool import BaseTool
from .helpers import find_point_in_glyph, round_point, coords_in_range


class SelectTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.selection = None
        self.select_rect = None
        self.drag_origin = (0, 0)

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            pos = canvas.mouse_pos
            glyph = canvas.glyph
            self.drag_origin = pos
            locked_pos = round_point(pos)
            point, contour = find_point_in_glyph(glyph, locked_pos)
            if event.type == Gdk.EventType.BUTTON_PRESS:
                pos_is_in_range = coords_in_range(pos, locked_pos)
                if pos_is_in_range and point is not None:
                    if event.state & Gdk.ModifierType.SHIFT_MASK:
                        selection = glyph.selection
                        if point.selected:
                            selection.remove(point)
                        else:
                            selection.add(point)
                    else:
                        if point.selected:
                            selection = glyph.selection
                        else:
                            selection = set()
                            selection.add(point)
                    self.selection = selection
                else:
                    self.select_rect = (canvas.mouse_pos, canvas.mouse_pos)

            elif event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                if point is None:
                    for contour in reversed(glyph):
                        index = contour.get_pos_on_path(pos)
                        if index is not None:
                            point = contour.insert_new_point(index, locked_pos)
                            self.selection = set()
                            self.selection.add(point)
                            self.select_rect = None
                            break

    def on_mouse_move(self, canvas, event):
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            x, y = canvas.mouse_pos
            if self.select_rect is not None:
                self.select_rect = (self.select_rect[0], (x, y))
            else:
                glyph = canvas.glyph
                x, y = round_point((x, y))
                dx, dy = round_point(self.drag_origin)
                translation = (x - dx, y - dy)
                glyph.selection = self.selection
                if translation != (0, 0):
                    glyph.move_selected(translation)
                self.drag_origin = (x, y)

    def on_mouse_release(self, canvas, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            glyph = canvas.glyph
            if self.select_rect is not None:
                modifier = event.state & Gdk.ModifierType.SHIFT_MASK
                selection = glyph.selection if modifier else set()
                points = self.get_points_in_rect(glyph, self.select_rect)
                selection.update(points)
            else:
                selection = self.selection
            glyph.selection = selection
            self.select_rect = None

    def on_key_press(self, canvas, event):
        translations = {
            'Up': (0, -1),
            'Down': (0, 1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }
        key = Gdk.keyval_name(event.keyval)
        if key in translations:
            canvas.glyph.move_selected(translations[key])

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self):
        if self.selection is not None:
            for point in self.selection:
                point.selected = False
        self.selection = None
        self.select_rect = None
        self.drag_origin = (0, 0)

    def get_points_in_rect(self, glyph, rect):
        (sx, sy), (ex, ey) = rect
        if sx > ex:
            sx, ex = ex, sx
        if sy > ey:
            sy, ey = ey, sy
        points = set()
        for contour in glyph:
            for point in contour:
                x, y = point.x, point.y
                if sx < x < ex and sy < y < ey:
                    points.add(point)
        return points

    # ╭──────────────╮
    # │ DRAW METHODS │
    # ╰──────────────╯

    def draw_cursor(self, ctx, canvas):
        locked_pos = round_point(canvas.mouse_pos)
        if not coords_in_range(canvas.mouse_pos, locked_pos):
            return

        pt, contour = find_point_in_glyph(canvas.glyph, locked_pos)
        color = (1, 0, 106/255) if pt is not None else (0.13, 0.3, 0.89)
        scale = canvas.scale
        x, y = locked_pos
        ctx.set_source_rgb(*color)
        ctx.set_line_width(2 / scale)
        ctx.arc(x, y, 10 / scale, 0.0, 2 * pi)
        ctx.stroke()

    def draw_specific(self, ctx, canvas):
        if self.select_rect is not None:
            self.draw_selection_rectangle(ctx, canvas.scale)

    def draw_selection_rectangle(self, ctx, scale):
        (ox, oy), (ex, ey) = self.select_rect
        w, h = ex - ox, ey - oy
        ctx.set_source_rgb(0.13, 0.3, 0.89)
        ctx.set_line_width(2 / scale)
        ctx.rectangle(ox, oy, w, h)
        ctx.stroke()
