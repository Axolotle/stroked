from fontTools.pens.basePen import BasePen


class SVGPathPen(BasePen):
    def __init__(self, glyphSet=None):
        super().__init__(glyphSet=glyphSet)
        self._commands = []
        self._prev_command = None

    def get_commands(self):
        return ''.join(self._commands)

    def _moveTo(self, pt):
        self._commands.append('M{},{}'.format(*pt))
        self._prev_command = 'M'

    def _lineTo(self, pt):
        x, y = pt
        # Not sure if this is ok but would have need to duplicate same information
        prev_x, prev_y = self._BasePen__currentPoint
        if x == prev_x and y == prev_y:
            return
        elif x == prev_x:
            self._commands.append('V' + str(y))
            self._prev_command = 'V'
        elif y == prev_y:
            self._commands.append('H' + str(x))
            self._prev_command = 'H'
        elif self._prev_command == 'M':
            # TODO: replace ' {},{}' by explicit 'L{},{}' ?
            self._commands.append(' {},{}'.format(x, y))
            self._prev_command = None
        else:
            self._commands.append('L{},{}'.format(x, y))
            self._prev_command = 'L'

    def _closePath(self):
        self._commands.append('Z')
        self._prev_command = 'Z'

    def _endPath(self):
        self._prev_command = None
