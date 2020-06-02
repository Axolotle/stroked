from gi.repository import Gdk
from math import pi

from .base_tool import BaseTool
from .helpers import round_point, find_point_in_glyph


class PenTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.contour = None

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_mouse_press(self, canvas, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.add_point(canvas.glyph, round_point(canvas.mouse_pos))
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.reset()

    def on_mouse_move(self, canvas, event):
        coords = round_point(canvas.mouse_pos)
        contour = self.contour
        # Update the last point coordinates with the mouse rounded coordinates
        # if a contour is currently drawn.
        if contour:
            last_point = contour[-1]
            last_point.x, last_point.y = coords

    # ╭──────────────╮
    # │ TOOL METHODS │
    # ╰──────────────╯

    def reset(self):
        if self.contour:
            # Remove the last point that was following the mouse.
            contour = self.contour
            contour.removePoint(contour[-1])
            self.contour = None

    def add_point(self, glyph, coords):
        contour = self.contour
        last_point = contour[-1] if contour else None
        target_pt, target_ctr = find_point_in_glyph(glyph, coords,
                                                    ignore=last_point)
        on_edge = target_ctr.is_edge_point(target_pt) if target_pt else False

        if contour is None:
            # If
            if target_pt and on_edge:
                if target_pt == target_ctr[0]:
                    target_ctr.reverse()
                contour = target_ctr
            else:
                contour = glyph.instantiateContour()
                glyph.appendContour(contour)
                contour.addPoint(coords, 'move')
            contour.addPoint(coords, 'line')
            self.contour = contour
        else:
            # Merge the current contour with the targeted one since
            # the targeted point is the first or last point.
            if target_pt and contour != target_ctr and on_edge:
                # If targeted contour is in the wrong direction, reverse it.
                if target_pt == target_ctr[-1]:
                    target_ctr.reverse()
                # Remove the last point that was following the mouse.
                contour.removePoint(contour[-1])
                contour.merge(target_ctr)
                glyph.removeContour(target_ctr)
                self.contour = None
            # Targeted point is the first point of the current contour,
            # close the contour.
            elif target_pt and target_pt == contour[0]:
                # Remove the last point that was following the mouse.
                contour.removePoint(contour[-1])
                # Change first point segmentType from 'move' to 'line'
                # to close the contour.
                contour[0].segmentType = 'line'
                self.contour = None
            # Simply add a new point at coordinates that will be the new point
            # updated by the mouse move since last point should already be
            # at the correct coordinates.
            else:
                contour.addPoint(coords, 'line')

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
