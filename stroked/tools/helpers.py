

def get_point_in_glyph(glyph, pt):
    x, y = pt
    for contour in glyph:
        for point in contour:
            if x == point.x and y == point.y:
                return point
    return None


def get_point_in_contour(contour, pt):
    x, y = pt
    for point in contour:
        if x == point.x and y == point.y:
            return point
    return None
