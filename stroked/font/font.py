import os
from datetime import date

from defcon import Font as DefFont

from stroked.font.layer_set import LayerSet
from stroked.font.glyph import Glyph
from stroked.font.contour import Contour
from stroked.font.point import Point


class Font(DefFont):
    def __init__(self, path=None):
        super().__init__(
            path=path,
            layerSetClass=LayerSet,
            glyphClass=Glyph, glyphContourClass=Contour, glyphPointClass=Point)

        if path is None:
            self.set_default()
        else:
            if 'space.autre.stroked' not in self.lib:
                self.lib['space.autre.stroked'] = {}
            self.slib = self.lib['space.autre.stroked']

        self._active_master_name = self._layers.defaultLayer.name

    @property
    def active_master(self):
        name = self._active_master_name
        if name is not None and name in self._layers:
            return self._layers[name]
        return None

    @active_master.setter
    def active_master(self, name):
        self._active_master_name = name

    @property
    def masters(self):
        return [layer for layer in self._layers if 'master.' in layer.name]

    @property
    def instances(self):
        return self.slib['instances']

    @property
    def grid(self):
        return (self.slib['gridWidth'], self.slib['gridHeight'])

    def set_default(self):
        self.info.openTypeHeadCreated = '{:%Y/%m/%d %H:%M:%S}'.format(
            date.today())
        self.info.versionMajor = 1
        self.info.versionMinor = 0
        self.info.openTypeNameVersion = 'Version: 1.000'
        self.lib['space.autre.stroked'] = {}
        self.slib = self.lib['space.autre.stroked']
        self.slib['gridWidth'] = 5
        self.slib['gridHeight'] = 7

        self._layers.disableNotifications()
        del self._layers['public.default']
        base_master = self.add_master(name='Regular')
        self._layers.defaultLayer = base_master
        self._layers.dirty = False
        self._layers.enableNotifications()

        self.slib['instances'] = {}
        self.add_instance(name='Regular')

        glyph_order = []
        for uni in range(32, 127):
            name = chr(uni)
            glyph = base_master.newGlyph(name)
            glyph.unicodes = [uni]
            glyph.width = self.slib['gridWidth']
            glyph_order.append(name)
        self.glyphOrder = glyph_order

    def add_master(self, name='New Layer'):
        master = self.newLayer('master.' + name)
        master.disableNotifications()
        master.lib['space.autre.stroked'] = {
            'weight': 400,
            'width': 100,
            'ascender': 5,
            'capHeight': 5,
            'xHeight': 3,
            'descender': -2,
        }

        glyph_names = self.glyphOrder
        for glyph_name in glyph_names:
            master.newGlyph(glyph_name)
        master.enableNotifications()
        return master

    def delete_master(self, name):
        master = self._layers['master.' + name]
        is_default = self._layers.defaultLayer == master
        del self._layers['master.' + name]
        if is_default:
            first_master = self._layers[self._layers.layerOrder[0]]
            self._layers.defaultLayer = first_master

    def add_instance(self, name='New Instance'):
        instances = self.slib['instances']
        instances[name] = {
            'style_name': name,
            'weight': 400,
            'width': 5,
            'is_bold': False,
            'is_italic': False,
            'related_instance': False,
            'linewidth': 1,
            'linejoin': 1,
            'linecap': 1,
            'single_point': 1
        }
        return instances[name]

    def delete_instance(self, name):
        instances = self.slib['instances']
        instances.pop(name)

    def export(self, path, format_type, masters=None):
        from stroked.pens.stroked_point_pen import ContourOffsetPointPen
        from ufo2ft import compileOTF, compileTTF

        format_types = ('otf', 'ttf', 'ufo')
        if format_type not in format_types:
            raise ValueError('Unknown format: {}'.format(format_type))
        if not os.path.isdir(path):
            raise OSError(2, os.strerror(2), path)

        if masters is None:
            masters = self.masters

        scale = 100
        for master in masters:
            source = self.get_master_as_source(master, scale=scale)
            for instance_data in self.instances.values():
                font = DefFont()
                info = dict(source['info'])
                lib = dict(source['lib'])

                info['styleName'] = instance_data['style_name']
                info['openTypeOS2WeightClass'] = instance_data['weight']
                info['openTypeOS2WidthClass'] = instance_data['width']

                font.info.setDataFromSerialization(info)
                font.lib.setDataFromSerialization(lib)

                for glyph in source['font']:
                    new_glyph = font.newGlyph(glyph.name)
                    new_glyph.unicodes = glyph.unicodes
                    out_pen = ContourOffsetPointPen(
                        new_glyph.getPen(),
                        linewidth=instance_data['linewidth'] * scale,
                        linecap=instance_data['linecap'],
                        pointcap=instance_data['single_point'],
                        linejoin=instance_data['linejoin'],
                    )
                    glyph.drawPoints(out_pen)
                    new_glyph.width = glyph.width

                filename = '{}-{}.{}'.format(
                    info['familyName'], info['styleName'], format_type
                ).replace(' ', '')
                if format_type in ('otf', 'ttf'):
                    func = compileOTF if format_type == 'otf' else compileTTF
                    compiled = func(font)
                    compiled.save(os.path.join(path, filename))
                elif format_type == 'ufo':
                    font.save(path=os.path.join(path, filename))

    def get_master_as_source(self, master, scale=100):
        """
        Returns a copy of a master as a defcon Font object.
        The font is scaled and coordinates are converted with UFO origin.
        Some generic attributes from self.lib, self.info and master.lib are
        also added.
        """
        from fontTools.pens.transformPen import TransformPointPen
        from fontTools.misc.transform import Transform

        info = self.info.getDataForSerialization()
        lib = self.lib.getDataForSerialization()
        master_lib = master.lib['space.autre.stroked']
        del lib['space.autre.stroked']

        font = DefFont()
        for attr in ('ascender', 'capHeight', 'xHeight', 'descender'):
            info[attr] = master_lib[attr] * scale
        info['unitsPerEm'] = info['ascender'] + abs(info['descender'])

        transformation = Transform(scale, 0, 0, -scale,
                                   0.5 * scale, info['ascender'] - 0.5 * scale)

        for glyph in master:
            new_glyph = font.newGlyph(glyph.name)
            new_glyph.unicodes = glyph.unicodes
            new_glyph.width = glyph.width * scale
            point_pen = new_glyph.getPointPen()
            transform_pen = TransformPointPen(point_pen, transformation)
            glyph.drawPoints(transform_pen)

        return {
            'font': font,
            'info': info,
            'lib': lib,
        }
