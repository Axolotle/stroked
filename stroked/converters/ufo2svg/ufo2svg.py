"""Generate a SVG font file from an UFO defcon-like object.
"""

from lxml.etree import Element, SubElement, tostring

from . import fontface_attrib, glyph_attrib

# This module is based on Tal Leming's archived ufo2svg lib:
# https://github.com/typesupply/ufo2svg


doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" >\n'


def get_fontface_attrib(ufo):
    """Returns a SVG font-face compliant dict with values extracted from the given UFO.
    """
    attrib = {}
    for setter_name in fontface_attrib.__all__:
        getattr(fontface_attrib, setter_name)(ufo, attrib)
    return attrib


def get_glyph_attrib(ufo_glyph):
    """Returns a SVG glyph compliant dict with values extracted from the given
    UFO's glyph.
    """
    attrib = {}
    for setter_name in glyph_attrib.__all__:
        getattr(glyph_attrib, setter_name)(ufo_glyph, attrib)
    return attrib


def get_missing_glyph_attrib(ufo):
    """Returns a SVG missing-glyph compliant dict with values extracted from the given
    UFO's `.notdef` glyph or from available UFO infos.
    """
    attrib = {}
    if '.notdef' in ufo:
        ufo_glyph = ufo['.notdef']
        glyph_attrib.set_horiz_adv_x(ufo_glyph, attrib)
        glyph_attrib.set_d(ufo_glyph, attrib)
    elif ufo.info.postscriptDefaultWidthX is not None:
        attrib['horiz-adv-x'] = str(ufo.info.postscriptDefaultWidthX)
    # Take care of `None` and `0` unitsPerEm.
    elif not ufo.info.unitsPerEm:
        attrib['horiz-adv-x'] = str(500)
    else:
        attrib['horiz-adv-x'] = str(int(ufo.info.unitsPerEm / 2))
    return attrib


def compile_UFO2SVG_font(ufo, path=None):
    """Convert an UFO defcon-like font object to a SVG font file.
    """
    svg = Element('svg', xmlns='http://www.w3.org/2000/svg', version='1.1')
    defs = SubElement(svg, 'defs')
    font = SubElement(defs, 'font', attrib={
        'id': ufo.info.familyName.replace(' ', ''), 'horiz-adv-x': '0'
    })

    # font-face
    SubElement(font, 'font-face', attrib=get_fontface_attrib(ufo))
    # missing-glyph
    SubElement(font, 'missing-glyph', attrib=get_missing_glyph_attrib(ufo))

    if ufo.glyphOrder is not None:
        glyph_order = ufo.glyphOrder
    else:
        glyph_order = sorted(ufo.keys())

    for glyph_name in glyph_order:
        if glyph_name == '.notdef':
            continue
        # glyph
        SubElement(font, 'glyph', attrib=get_glyph_attrib(ufo[glyph_name]))

    # TODO: add kerning handling

    output = tostring(
        svg, pretty_print=True, xml_declaration=True, encoding='UTF-8',
        doctype=doctype, standalone=False
    )

    if path is None:
        return output
    else:
        with open(path, 'wb') as input:
            input.write(output)
