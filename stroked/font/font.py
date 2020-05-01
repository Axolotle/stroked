from datetime import date

from defcon import Font as DefFont


class Font(DefFont):
    def __init__(self, path=None):
        super().__init__(path=path)

        if path is None:
            self.set_default()
        else:
            if 'space.autre.stroked' not in self.lib:
                self.lib['space.autre.stroked'] = {}
            self.slib = self.lib['space.autre.stroked']

        self._active_master = None

    @property
    def active_master(self):
        name = self._active_master
        if name is not None and name in self._layers:
            return self._layers[name]
        return None

    @active_master.setter
    def active_master(self, name):
        self._active_master = name

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

        glyph_order = []
        for glyph in range(32, 127):
            name = chr(glyph)
            base_master.newGlyph(name)
            glyph_order.append(name)
        self.glyphOrder = glyph_order

    def add_master(self, name='New Layer'):
        master = self.newLayer('master.' + name)
        master.lib = {
            'weight': 400,
            'width': 100,
            'ascender': 5,
            'capHeight': 5,
            'xHeight': 3,
            'descender': 2,
        }

        glyph_names = self.glyphOrder
        for glyph_name in glyph_names:
            master.newGlyph(glyph_name)

        return master

    def delete_master(self, name):
        master = self._layers['master.' + name]
        is_default = self._layers.defaultLayer == master
        del self._layers['master.' + name]
        if is_default:
            first_master = self._layers[self._layers.layerOrder[0]]
            self._layers.defaultLayer = first_master
