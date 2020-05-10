from defcon import Contour as DefContour

from .point import Point


class Contour(DefContour):
    def __init__(self, *args, **kwargs):
        if "pointClass" not in kwargs:
            kwargs["pointClass"] = Point
        super().__init__(*args, **kwargs)

    @property
    def selected(self):
        for point in self:
            if not point.selected:
                return False
        return True

    @selected.setter
    def selected(self, value):
        for point in self:
            point.selected = value

    @property
    def selection(self):
        selection = set()
        for point in self:
            if point.selected:
                selection.add(point)
        return selection

    @selection.setter
    def selection(self, selection):
        for point in self:
            point.selected = point in selection
