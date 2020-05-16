import math


def find_point_in_glyph(glyph, coordinates):
    x, y = coordinates
    for contour in reversed(glyph):
        for point in reversed(contour):
            if x == point.x and y == point.y:
                return (point, contour)
    return (None, None)


def round_point(pt):
    return (round(pt[0]), round(pt[1]))


def coords_in_range(coords, ref, threshold=0.25):
    vx, vy = (coords[0] - ref[0], coords[1] - ref[1])
    norm = math.sqrt(vx**2 + vy**2)
    if norm <= threshold:
        return True
    return False
