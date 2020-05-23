import math

from fontTools.pens.pointPen import PointToSegmentPen


_linejoins = ['miter', 'round', 'bevel']
_linecaps = ['butt', 'round', 'square']
_points = ['miter', 'round', 'square']


def rotate_vector(vx, vy, theta):
    cos, sin = math.cos(theta), math.sin(theta)
    return (cos * vx - sin * vy, sin * vx + cos * vy)


def set_vector_length(vx, vy, length):
    norm = math.hypot(vx, vy)
    if norm == 0:
        return (vx * length, vy * length)
    return (vx / norm * length, vy / norm * length)


def get_segment_projection(x0, y0, x1, y1, vx, vy):
    return ((x0 + vx, y0 + vy), (x1 + vx, y1 + vy))


def get_segment_intersection(ax, ay, bx, by, cx, cy, dx, dy, force=False):
    ix, iy = bx - ax, by - ay
    jx, jy = dx - cx, dy - cy
    div = ix * jy - iy * jx
    # check if i & j are not parallel
    if div != 0:
        # k = (j[0] * a[1] - j[0] * c[1] - j[1] * a[0] + j[1] * c[0]) / div
        # return Point(a + k * i)
        m = (ix * ay - ix * cy - iy * ax + iy * cx) / div
        # check if lines intersect
        if force or 0 < m < 1:
            return (cx + jx * m, cy + jy * m)
    return None


class StrokeToShapePointPen(PointToSegmentPen):
    '''
    Point pen that turn a stroke contour to a shape contour. The output may be
    a single contour in case of an initial opened contour or a double contour
    in case of an initial closed contour (the inner output contour is drawn
    in reversed order to clip the outer output contour).
    '''

    def __init__(self, segmentPen, outputImpliedClosingLine=False,
                 thickness=1, linejoin=2, linecap=2, point=2):
        super().__init__(segmentPen, outputImpliedClosingLine)

        self.inner_path = None
        self.outer_path = None

        # Methods binding
        self._linejoin = getattr(self, '_linejoin_' + _linejoins[linejoin])
        self._linecap = getattr(self, '_linecap_' + _linecaps[linecap])
        self._point = getattr(self, '_point_' + _points[point])
        self._offset = thickness/2

    def _flushContour(self, *contours):
        assert len(contours) >= 1
        pen = self.pen
        for segments in contours:
            pen.moveTo(segments[0][1][0][0])
            n = len(segments)
            for i in range(1, n):
                segmentType, points = segments[i]
                points = [pt for pt, smooth, name, kwargs in points]
                if segmentType == "line":
                    pen.lineTo(points[0])
            # Do not endPath() to allow next contour to clip the previous one
            pen.closePath()
        pen.endPath()

    def _stroke_to_path(self, points):
        assert len(points) >= 1
        assert self.inner_path is None
        assert self.outer_path is None

        self.outer_path = []
        self.inner_path = []
        n = len(points)

        # Remove duplicated point if last points are the same.
        if n > 1 and points[-1][0] == points[-2][0]:
            del points[-1]
            n -= 1

        if n == 1:
            # Single point case, just draw the desired shape at its position.
            self._point(*points[0][0])
            self._flushContour(self.outer_path)
            return

        if points[0][1] == 'move':
            closed = False
            self._linecap(*points[0][0], *points[1][0])
            indices = range(1, n - 1)
        else:
            closed = True
            indices = range(-1, n - 1)

        for i in indices:
            self._linejoin(*points[i - 1][0], *points[i][0], *points[i + 1][0])

        self.inner_path.reverse()
        if closed:
            # flush the two contours separately
            self._flushContour(self.outer_path, self.inner_path)
        else:
            self._linecap(*points[-1][0], *points[-2][0])
            # flush the merged contours
            self._flushContour(self.outer_path + self.inner_path)

    def endPath(self):
        assert self.currentPath is not None
        points = self.currentPath
        self.currentPath = None
        self._stroke_to_path(points)
        self.outer_path = None
        self.inner_path = None

    def _linecap_square(self, x0, y0, x1, y1):
        path = self.outer_path
        # set the lenght of the vector of p0 to p1 to the desired thickness
        v0x, v0y = set_vector_length(x1 - x0, y1 - y0, self._offset)
        # get a version of it rotated by 90°
        v1x, v1y = rotate_vector(v0x, v0y, math.pi / 2)
        # define the 2 new point position by moving the base point
        p0 = (x0 - v0x - v1x, y0 - v0y - v1y)
        p1 = (x0 - v0x + v1x, y0 - v0y + v1y)
        path.append(('line', [(p0, False, None, {})]))
        path.append(('line', [(p1, False, None, {})]))

    def _linejoin_bevel(self, x0, y0, x1, y1, x2, y2):
        # (x0, y0) is point a, etc.
        # set the lenght of the vector of p0 to p1 to the desired thickness
        v0x, v0y = set_vector_length(x1 - x0, y1 - y0, self._offset)
        v0x, v0y = rotate_vector(v0x, v0y, math.pi / 2)
        v1x, v1y = set_vector_length(x2 - x1, y2 - y1, self._offset)
        v1x, v1y = rotate_vector(v1x, v1y, math.pi / 2)

        for d, path in ((1, self.outer_path), (-1, self.inner_path)):
            # get the segment (p0, p1) parallel to the segment (a, b)
            # and the segment (p2, p3) parallel to the segment (b, c)
            p0, p1 = get_segment_projection(x0, y0, x1, y1, v0x * d, v0y * d)
            p2, p3 = get_segment_projection(x1, y1, x2, y2, v1x * d, v1y * d)
            intersection = get_segment_intersection(*p0, *p1, *p2, *p3)
            if intersection is None:
                # no intersection, add the points closed to point b
                path.append(('line', [(p1, False, None, {})]))
                path.append(('line', [(p2, False, None, {})]))
            else:
                # add the intersection point
                path.append(('line', [(intersection, False, None, {})]))

    def _point_square(self, x, y):
        offset = self._offset
        path = self.outer_path
        vs = [(offset, -offset), (-offset, -offset),
              (-offset, offset), (offset, offset)]
        for vx, vy in vs:
            path.append(('line', [((x + vx, y + vy), False, None, {})]))
