from defcon import Contour as DefContour

from .point import Point


def coords_are_between_points(p0, p1, coords, e=0.25):
    """
    Returns a boolean indicating if the coordinates lies on the segment
    (p0, p1).
    """
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
        """
        A boolean indicating if all points in contour are selected.
        """
        for point in self:
            if not point.selected:
                return False
        return True

    @selected.setter
    def selected(self, value):
        """
        Sets the selected attribute of all points to **True** or **False**.
        """
        for point in self:
            point.selected = value

    @property
    def selection(self):
        """
        Get the points with `selected` attribute set to True as a `set`.
        """
        selection = set()
        for point in self:
            if point.selected:
                selection.add(point)
        return selection

    @selection.setter
    def selection(self, selection):
        """
        Sets the selected attribute of all points to **True** or **False**
        depending of the given selection.
        """
        for point in self:
            point.selected = point in selection

    def is_edge_point(self, point):
        """
        Returns a boolean indicating if `point` is the first or last point of
        this contour in case of a open contour.
        """
        return self.open and (
            point.segmentType == 'move' or point == self._points[-1])

    def get_pos_on_path(self, coords):
        """
        Returns the index at where a point could be inserted if the **coords**
        lies on one of this contour's segments. Else, returns `None`.
        """
        for i in range(1, len(self)):
            if coords_are_between_points(self[i-1], self[i], coords):
                return i
        return None

    def insert_new_point(self, index, coords, segmentType='line'):
        """
        Insert a `Point` into the contour at **index** with **coords**.
        It differs from `insertPoint()` in that it creates a `Point` object.

        This will post *Contour.PointsChanged* and *Contour.Changed*
        notifications.
        """
        point = self._pointClass(coords, segmentType=segmentType)
        self.insertPoint(index, point)
        return point

    def merge(self, contour):
        """
        Merge the given `Contour` with `self` by adding its point to self.
        """
        # NOTE: should copy points instead of appending the existing ones ?
        for point in contour:
            self.appendPoint(point)

    def move_selected(self, values):
        """
        Move the points that are `selected` by (x, y).

        This will post *Contour.PointsChanged* and *Contour.Changed*
        notifications.
        """
        for point in self.selection:
            point.move(values)
        self.postNotification('Contour.PointsChanged')
        self.dirty = True
