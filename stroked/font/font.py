from datetime import date

from defcon import Font as DefFont


class Font(DefFont):
    def __init__(self, path=None):
        super().__init__(path=path)

        if path is None:
            self.set_default()

    def set_default(self):
        self.info.openTypeHeadCreated = '{:%Y/%m/%d %H:%M:%S}'.format(
            date.today())
        self.info.versionMajor = 1
        self.info.versionMinor = 0
        self.info.openTypeNameVersion = 'Version: 1.000'
        self.lib['gridWidth'] = 5
        self.lib['gridHeight'] = 7

        self._layers.disableNotifications()
        del self._layers['public.default']
        base_master = self.newLayer('master.regular')
        self._layers.defaultLayer = base_master
        self._layers.dirty = False
        self.lib['masters'] = {}
        self.lib['masters']['regular'] = {
            'weight': 400,
            'width': 100,
            'ascender': 5,
            'capHeight': 5,
            'xHeight': 3,
            'descender': 2,
        }
