from fontTools.pens.basePen import BasePen


class CairoStrokePen(BasePen):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        # avoid linejoin and linecap problems
        self.ctx.set_tolerance(1)
        ctx.set_source_rgb(0, 1, 0.5)

    def _moveTo(self, pt):
        self.ctx.move_to(*pt)

    def _lineTo(self, pt):
        self.ctx.line_to(*pt)

    def _closePath(self):
        self.ctx.close_path()
        self.endPath()

    def _endPath(self):
        self.ctx.stroke()


class CairoShapePen(BasePen):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def _moveTo(self, pt):
        self.ctx.move_to(*pt)

    def _lineTo(self, pt):
        self.ctx.line_to(*pt)

    def _closePath(self):
        self.ctx.close_path()
        self.endPath()

    def _endPath(self):
        self.ctx.stroke()
