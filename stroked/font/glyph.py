from defcon import Glyph as DefGlyph


class Glyph(DefGlyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def selected(self):
        for contour in self:
            if not contour.selected:
                return False
        return True

    @selected.setter
    def selected(self, value):
        for contour in self:
            contour.selected = value

    @property
    def selection(self):
        selection = set()
        for contour in self:
            selection.update(contour.selection)
        return selection

    @selection.setter
    def selection(self, selection):
        for contour in self:
            contour.selected = contour in selection
