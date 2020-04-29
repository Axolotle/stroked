from datetime import date

from defcon import Font as DefFont


class Font(DefFont):
    def __init__(self, path=None):
        super().__init__(path=path)

        if path is None:
            self.set_default()
        else:
            self.slib = self.lib['space.autre.stroked']

    def set_default(self):
        self.info.openTypeHeadCreated = '{:%Y/%m/%d %H:%M:%S}'.format(
            date.today())
        self.info.versionMajor = 1
        self.info.versionMinor = 0
        self.info.openTypeNameVersion = 'Version: 1.000'
        self.slib = {}
        self.lib['space.autre.stroked'] = self.slib
        self.slib['gridWidth'] = 5
        self.slib['gridHeight'] = 7
        self.slib['masters'] = {}

        self._layers.disableNotifications()
        del self._layers['public.default']
        base_master = self.add_master(name='Regular')
        self._layers.defaultLayer = base_master
        self._layers.dirty = False

    def add_master(self, name='New Layer'):
        self.slib['masters'][name] = {
            'weight': 400,
            'width': 100,
            'ascender': 5,
            'capHeight': 5,
            'xHeight': 3,
            'descender': 2,
        }
        return self.newLayer('master.' + name)

    def delete_master(self, name):
        master = self._layers['master.' + name]
        is_default = self._layers.defaultLayer == master
        del self.slib['masters'][name]
        del self._layers['master.' + name]
        if is_default:
            first_master = self._layers[self._layers.layerOrder[0]]
            self._layers.defaultLayer = first_master
