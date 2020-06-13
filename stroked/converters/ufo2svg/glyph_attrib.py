"""Extracts SVG glyph attributes from UFO glyph object

This module contains a list a function that extracts UFO informations and
translates them into SVG glyph attributes.
You can import this module and iterate over its `__all__` property to execute
every functions.

List and meaning of the possible `<glyph />` attributes are defined in w3c specs:
https://www.w3.org/TR/SVG11/fonts.html#GlyphElement
"""

from stroked.pens.svg_pen import SVGPathPen

__all__ = [
    'set_unicode',
    'set_glyph_name',
    'set_horiz_adv_x',
    # 'set_vert_origin_x',
    # 'set_vert_origin_y',
    # 'set_vert_adv_y',
    # 'set_orientation',
    # 'set_arabic_form',
    # 'set_lang',
    'set_d',
]


def set_unicode(ufo_glyph, attrib):
    if ufo_glyph.unicodes:
        attrib['unicode'] = ''.join([chr(code_pt) for code_pt in ufo_glyph.unicodes])


def set_glyph_name(ufo_glyph, attrib):
    assert ufo_glyph.name is not None
    attrib['glyph-name'] = ufo_glyph.name


def set_horiz_adv_x(ufo_glyph, attrib):
    if ufo_glyph.width is not None:
        attrib['horiz-adv-x'] = str(ufo_glyph.width)


def set_d(ufo_glyph, attrib):
    pen = SVGPathPen(glyphSet=ufo_glyph.getParent())
    ufo_glyph.draw(pen)
    attrib['d'] = pen.get_commands()
