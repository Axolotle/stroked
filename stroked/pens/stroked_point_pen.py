from enum import Enum
import math

from fontTools.pens.pointPen import AbstractPointPen

_pi = 3.141592653589793238
_two_pi = _pi * 2
_arc_tolerance = 0.25
_miter_limit = 4.0


class Linecap(Enum):
    BUTT = 0
    ROUND = 1
    SQUARE = 2


class Linejoin(Enum):
    MITER = 0
    ROUND = 1
    BEVEL = 2


class Pointcap(Enum):
    ROUND = 1
    SQUARE = 2


def get_unit_normal(p1, p2):
    x1, y1, x2, y2 = *p1, *p2
    if x1 == x2 and y1 == y2:
        return (0, 0)
    vx, vy = x2 - x1, y2 - y1
    norm_factor = 1.0 / math.sqrt(vx*vx + vy*vy)

    return (vy * norm_factor, -vx * norm_factor)


# Most of the code related to the offset calculation is traduced from or
# inspired by Angus Johnson's Clipper library, C++ version.
# http://www.angusj.com/delphi/clipper.php
# I could have used the python wrapper Pyclipper but i need to add some
# custom linejoins/linecaps/pointcaps
class ContourOffsetPointPen(AbstractPointPen):
    '''
    Point pen that turn a stroke contour to a shape contour. The output may be
    a single contour in case of an initial opened contour or a double contour
    in case of an initial closed contour (the inner output contour is drawn
    in reversed order to clip the outer output contour).
    '''

    def __init__(self, segmentPen,
                 thickness=1, linejoin=Linejoin.ROUND, linecap=Linecap.ROUND,
                 pointcap=Pointcap.ROUND,
                 miter_lim=_miter_limit, arc_tol=_arc_tolerance):
        self.pen = segmentPen

        self.data = []

        self.input_path = None
        self.output_paths = None
        self.current_path = None
        self.normals = None

        self.linejoin_type = linejoin
        self.linecap_type = linecap
        self.pointcap_type = pointcap

        self.delta = thickness * 100 / 2
        self.miter_lim = 2 / (miter_lim * miter_lim) if miter_lim > 2 else 0.5
        self.lowest_x = -1

        y = None
        if arc_tol < 0:
            y = _arc_tolerance
        elif arc_tol > abs(self.delta) * _arc_tolerance:
            y = abs(self.delta) * _arc_tolerance
        else:
            y = arc_tol

        steps = _pi / math.acos(1 - y / abs(self.delta))
        if (steps > abs(self.delta) * _pi):
            steps = abs(self.delta) * _pi
        self.sin = math.sin(_two_pi / steps)
        self.cos = math.cos(_two_pi / steps)
        self.steps_per_rad = steps / _two_pi
        self.steps = steps

        if self.delta < 0:
            self.sin = -self.sin

    def beginPath(self, identifier=None, **kwargs):
        assert self.input_path is None
        self.input_path = []

    def get_data(self):
        return self.data

    def _flushContour(self):
        assert len(self.output_paths) >= 1
        pen = self.pen
        for path in self.output_paths:
            assert len(path) >= 1
            x, y = path[0][0]/100, path[0][1]/100
            self.data.append((x, y))
            pen.moveTo((x, y))
            n = len(path)
            for i in range(1, n):
                x, y = path[i][0]/100, path[i][1]/100
                self.data.append((x, y))
                pen.lineTo((x, y))
            pen.closePath()

    def endPath(self):
        assert self.input_path is not None
        self._offset_path()
        self.input_path = None
        self.output_paths = None
        self.current_path = None

    def addPoint(self, pt, segmentType=None, smooth=False, name=None,
                 identifier=None, **kwargs):
        self.input_path.append(((pt[0]*100, pt[1]*100), segmentType))

    def _offset_path(self):
        points = self.input_path
        assert len(points) >= 1
        assert self.output_paths is None
        assert self.current_path is None

        self.output_paths = []
        self.current_path = []
        n = len(points)
        closed = points[0][1] != 'move'

        if n == 1:
            if self.pointcap_type == Pointcap.SQUARE:
                self._do_pointcap_square(0)
            elif self.pointcap_type == Pointcap.ROUND:
                self._do_pointcap_round(0)
            else:
                return
            self.output_paths.append(self.current_path)
            self._flushContour()
            return

        # build normals
        self.normals = []
        for i in range(n - 1):
            self.normals.append(get_unit_normal(points[i][0], points[i + 1][0]))
        if closed:
            self.normals.append(get_unit_normal(points[-1][0], points[0][0]))
        else:
            self.normals.append(self.normals[n - 2])

        if closed:
            k = n - 1
            for j in range(n):
                k = self._offset_point(j, k, self.linejoin_type)
            self.output_paths.append(self.current_path)
            self.current_path = []

            # re-build normals ...
            normals = self.normals
            last_un = normals[-1]
            for i in range(n - 1, 0, -1):
                self.normals[i] = (-normals[i - 1][0], -normals[i - 1][1])
            self.normals[0] = (-last_un[0], -last_un[1])

            k = 0
            for j in range(n - 1, -1, -1):
                k = self._offset_point(j, k, self.linejoin_type)
            self.output_paths.append(self.current_path)
        else:
            k = 0
            for j in range(1, n - 1):
                k = self._offset_point(j, k, self.linejoin_type)

            if self.linecap_type == Linecap.BUTT:
                self._do_linecap_butt(-1)
            else:
                j, k = n - 1, n - 2
                sinA = 0
                last_un = self.normals[-1]  # normals[j]
                self.normals[-1] = (-last_un[0], -last_un[1])
                if self.linecap_type == Linecap.ROUND:
                    self._do_round(j, k, sinA)
                else:
                    self._do_square(j, k, sinA)

            # re-build normals ...
            normals = self.normals
            for i in range(n - 1, 0, -1):
                self.normals[i] = (-normals[i - 1][0], -normals[i - 1][1])
            self.normals[0] = (-normals[1][0], -normals[1][1])

            k = n - 1
            for j in range(k - 1, 0, -1):
                k = self._offset_point(j, k, self.linejoin_type)

            if self.linecap_type == Linecap.BUTT:
                self._do_linecap_butt(0)
            else:
                k = 1
                sinA = 0
                if self.linecap_type == Linecap.SQUARE:
                    self._do_square(0, 1, sinA)
                else:
                    self._do_round(0, 1, sinA)
            self.output_paths.append(self.current_path)
        self._flushContour()

    def _offset_point(self, j, k, join_type):
        d = self.delta
        path = self.current_path
        x, y = self.input_path[j][0]
        unx1, uny1 = self.normals[j]
        unx2, uny2 = self.normals[k]
        # cross product
        sinA = (unx2 * uny1 - unx1 * uny2)
        if abs(sinA * d) < 1.0:
            # dot product ...
            cosA = (unx2 * unx1 + uny1 * uny2)
            if cosA > 0:  # angle => 0 degrees
                path.append((round(x + unx2 * d), round(y + uny2 * d)))
                return k
            # else angle => 180 degrees
        elif sinA > 1:
            sinA = 1.0
        elif sinA < -1:
            sinA = -1.0

        if sinA * d < 0:
            path.append((round(x + unx2 * d), round(y + uny2 * d)))
            path.append((x, y))
            path.append((round(x + unx1 * d), round(y + uny1 * d)))
        else:
            if join_type == Linejoin.MITER:
                r = 1 + (unx1 * unx2 + uny1 * uny2)
                if r >= self.miter_lim:
                    self._do_miter(j, k, r)
                else:
                    self._do_square(j, k, sinA)
            elif join_type == Linejoin.BEVEL:
                self._do_square(j, k, sinA)
            elif join_type == Linejoin.ROUND:
                self._do_round(j, k, sinA)
        return j

    # ╭──────────────────────────────────╮
    # │ LINEJOIN/LINECAP GENERIC METHODS │
    # ╰──────────────────────────────────╯

    def _do_miter(self, j, k, r):
        q = self.delta / r
        x, y = self.input_path[j][0]
        unx1, uny1 = self.normals[j]
        unx2, uny2 = self.normals[k]
        self.current_path.append((round(x + (unx2 + unx1) * q),
                                  round(y + (uny2 + uny1) * q)))

    def _do_square(self, j, k, sinA):
        d = self.delta
        path = self.current_path
        x, y = self.input_path[j][0]
        unx1, uny1 = self.normals[j]
        unx2, uny2 = self.normals[k]
        cosA = unx2 * unx1 + uny2 * uny1
        dx = math.tan(math.atan2(sinA, cosA) / 4)
        path.append((round(x + d * (unx2 - uny2 * dx)),
                     round(y + d * (uny2 + unx2 * dx))))
        path.append((round(x + d * (unx1 + uny1 * dx)),
                     round(y + d * (uny1 - unx1 * dx))))

    def _do_round(self, j, k, sinA):
        d = self.delta
        path = self.current_path
        x, y = self.input_path[j][0]
        unx1, uny1 = self.normals[j]
        unx2, uny2 = self.normals[k]

        cosA = unx2 * unx1 + uny2 * uny1
        a = math.atan2(sinA, cosA)
        steps = max(round(self.steps_per_rad * abs(a)), 1)

        dx = unx2
        dy = uny2
        cos, sin = self.cos, self.sin
        for i in range(steps):
            path.append((round(x + dx * d), round(y + dy * d)))
            dx, dy = dx * cos - sin * dy, dx * sin + dy * cos

        path.append((round(x + unx1 * d), round(y + uny1 * d)))

    # ╭───────────────────────────╮
    # │ POINTCAP SPECIFIC METHODS │
    # ╰───────────────────────────╯

    def _do_pointcap_square(self, i):
        d = self.delta
        path = self.current_path
        x, y = self.input_path[i][0]
        vectors = [(-d, -d), (d, -d), (d, d), (-d, d)]
        for vx, vy in vectors:
            path.append((round(x + vx), round(y + vy)))

    def _do_pointcap_round(self, i):
        d = self.delta
        path = self.current_path
        x, y = self.input_path[i][0]
        dx = 1.0
        dy = 0.0
        cos, sin = self.cos, self.sin
        for i in range(round(self.steps)):
            path.append((round(x + dx * d), round(y + dy * d)))
            dx, dy = dx * cos - sin * dy, dx * sin + dy * cos

    # ╭──────────────────────────╮
    # │ LINECAP SPECIFIC METHODS │
    # ╰──────────────────────────╯

    def _do_linecap_butt(self, i):
        d = self.delta
        path = self.current_path
        x, y = self.input_path[i][0]
        unx, uny = self.normals[i]
        a = (round(x - unx * d), round(y - uny * d))
        b = (round(x + unx * d), round(y + uny * d))
        if i == 0:
            path.append(a)
            path.append(b)
        else:
            path.append(b)
            path.append(a)
