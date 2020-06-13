"""Extracts SVG font-face attributes from UFO defcon-like object

This module contains a list a function that extracts UFO informations and
translates them into SVG font-face attributes.
You can import this module and iterate over its `__all__` property to execute
every functions.

List and meaning of the possible `<font-face />` attributes are defined in w3c specs:
https://www.w3.org/TR/SVG11/fonts.html#FontFaceElement
"""


__all__ = [
    'set_font_family',
    'set_font_style',
    # 'set_font_variant',
    'set_font_weight',
    'set_font_stretch',
    # 'set_font_size',
    # 'set_unicode_range',
    'set_units_per_em',
    # 'set_panose_1',
    # 'set_stemv',
    # 'set_stemh',
    # 'set_slope',
    'set_cap_height',
    'set_x_height',
    # 'set_accent_height',
    'set_ascent',
    'set_descent',
    # 'set_widths',
    'set_bbox',
    # 'set_ideographic',
    # 'set_alphabetic',
    # 'set_mathematical',
    # 'set_hanging',
    # 'set_v_ideographic',
    # 'set_v_alphabetic',
    # 'set_v_mathematical',
    # 'set_v_hanging',
    # 'set_underline_position',
    # 'set_underline_thickness',
    # 'set_strikethrough_position',
    # 'set_strikethrough_thickness',
    # 'set_overline_position',
    # 'set_overline_thickness',
]


def set_font_family(ufo, attrib):
    if ufo.info.familyName is not None:
        attrib['family-name'] = ufo.info.familyName


def set_font_style(ufo, attrib):
    if ufo.info.styleMapStyleName is not None:
        if 'italic' in ufo.info.styleMapStyleName:
            attrib['font-style'] = 'italic'
        else:
            attrib['font-style'] = 'normal'


def set_font_weight(ufo, attrib):
    if ufo.info.openTypeOS2WeightClass is not None:
        attrib['font-weight'] = str(ufo.info.openTypeOS2WeightClass)


def set_font_stretch(ufo, attrib):
    width_class = ufo.info.openTypeOS2WidthClass
    if width_class is None:
        return
    if 1 <= width_class <= 9:
        options = (
            'ultra-condensed', 'extra-condensed', 'condensed', 'semi-condensed',
            'normal', 'semi-expanded', 'expanded', 'extra-expanded', 'ultra-expanded'
        )
        attrib['font-stretch'] = options[width_class - 1]


def set_units_per_em(ufo, attrib):
    if ufo.info.unitsPerEm is not None:
        attrib['units-per-em'] = str(ufo.info.unitsPerEm)


def set_cap_height(ufo, attrib):
    if ufo.info.capHeight is not None:
        attrib['cap-height'] = str(ufo.info.capHeight)


def set_x_height(ufo, attrib):
    if ufo.info.xHeight is not None:
        attrib['x-height'] = str(ufo.info.xHeight)


def set_ascent(ufo, attrib):
    if ufo.info.ascender is not None:
        attrib['ascent'] = str(ufo.info.ascender)


def set_descent(ufo, attrib):
    if ufo.info.descender is not None:
        attrib['descent'] = str(ufo.info.descender)


def set_bbox(ufo, attrib):
    bounds = ufo.bounds
    if bounds is None:
        bounds = (0, 0, 0, 0)
    attrib['bbox'] = ' '.join([str(n) for n in bounds])
