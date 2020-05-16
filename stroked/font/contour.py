from defcon import Contour as DefContour

from .point import Point


def coords_are_between_points(p0, p1, coords, e=0.25):
    # combo from https://stackoverflow.com/q/328107
    # e is an arbitrary epsilon (error margin)
    x, y = coords
    x0, y0 = p0.x, p0.y
    x1, y1 = p1.x, p1.y
    cross_product = (y - y0) * (x1 - x0) - (x - x0) * (y1 - y0)
    return (abs(cross_product) < e
            and min(x0, x1) - e <= x <= max(x0, x1) + e
            and min(y0, y1) - e <= y <= max(y0, y1) + e)


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

    def is_edge_point(self, point):
        return point.segmentType == 'move' or point == self[-1]

    def get_pos_on_path(self, coords):
        for i in range(1, len(self)):
            if coords_are_between_points(self[i-1], self[i], coords):
                return i
        return None

    def insert_point(self, index, coords):
        point = self._pointClass(coords, segmentType='line')
        self.insertPoint(index, point)
        return point

    def merge(self, contour):
        contour.removePoint(contour[0])
        for point in contour:
            self.appendPoint(point)
        contour.glyph.removeContour(contour)
