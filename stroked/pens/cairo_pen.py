from fontTools.pens.basePen import BasePen


class CairoPen(BasePen):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def _moveTo(self, pt):
        self.ctx.move_to(*pt)

    def _lineTo(self, pt):
        self.ctx.line_to(*pt)

    def _endPath(self):
        self.ctx.stroke()
