

def find_point_in_glyph(glyph, coordinates):
    x, y = coordinates
    for contour in reversed(glyph):
        for point in reversed(contour):
            if x == point.x and y == point.y:
                return (point, contour)
    return (None, None)
