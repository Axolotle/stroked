from defcon import Glyph as DefGlyph


class Glyph(DefGlyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def selected(self):
        """
        A boolean indicating if all contours are selected.
        """
        for contour in self:
            if not contour.selected:
                return False
        return True

    @selected.setter
    def selected(self, value):
        """
        Sets the selected attribute of all contours to **True** or **False**.
        """
        for contour in self:
            contour.selected = value

    @property
    def selection(self):
        """
        Get the points of all contours that are selected as a `set`.
        """
        selection = set()
        for contour in self:
            selection.update(contour.selection)
        return selection

    @selection.setter
    def selection(self, selection):
        """
        Sets the selected attribute of all points of all contours to **True**
        or **False** depending of the given selection.
        """
        for contour in self:
            contour.selection = selection

    def move_selected(self, values):
        """
        Move the points of all contours that are selected by (x, y).

        This posts a *Glyph.Changed* notification.
        """
        for contour in self:
            contour.move_selected(values)
