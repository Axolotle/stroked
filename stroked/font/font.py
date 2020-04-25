from datetime import date

from defcon import Font as DefFont


class Font(DefFont):
    def __init__(self, path=None):
        super().__init__(path=path)
        if path is None:
            self.info.openTypeHeadCreated = '{:%Y/%m/%d %H:%M:%S}'.format(
                date.today())
            self.info.versionMajor = 1
            self.info.versionMinor = 0
            self.info.openTypeNameVersion = 'Version: 1.000'
            self.lib['gridWidth'] = 5
            self.lib['gridHeight'] = 7
