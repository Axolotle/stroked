from datetime import date

from defcon import Font as DefFont


class Font(DefFont):
    def __init__(self):
        super().__init__()

        self.info.openTypeHeadCreated = '{:%Y/%m/%d %H:%M:%S}'.format(
            date.today())
