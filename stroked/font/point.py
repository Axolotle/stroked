from defcon import Point as DefPoint


class Point(DefPoint):
    def __init__(self, coordinates, selected=False, **kwargs):
        super().__init__(coordinates, **kwargs)
        self._selected = selected

    def __repr__(self):
        return ('<{} position: ({}, {}) type: {} smooth: {}'
                'name: {} identifier: {}, selected: {}>').format(
            self.__class__.__name__, self.x, self.y,
            str(self.segmentType), str(self.smooth),
            str(self.name), str(self.identifier),
            str(self._selected))

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
