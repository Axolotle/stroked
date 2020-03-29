import weakref

from .base_tool import BaseTool


class SelectTool(BaseTool):
    def __init__(self):
        super().__init__()
        self._glyph = None

    def set_glyph(self, glyph):
        self._glyph = weakref.ref(glyph)
