

def get_point_in_glyph(pt, glyph):
    for contour in glyph:
        for point in contour:
            if pt[0] == point.x and pt[1] == point.y:
                return point
    return None


def get_point_in_contour(pt, contour):
    for point in contour:
        if pt[0] == point.x and pt[1] == point.y:
            return point
    return None
