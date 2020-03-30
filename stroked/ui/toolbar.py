import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject

from stroked.tools import SelectTool, PenTool


class Toolbar(Gtk.Toolbar):
    __gtype_name__ = 'Toolbar'

    def __init__(self):
        super().__init__()
        self._current_tool = None
        self.tools = [
            SelectTool(),
            PenTool()
        ]

    def do_realize(self):
        Gtk.Toolbar.do_realize(self)
        self.set_tools()

    @GObject.Property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, value):
        self._current_tool = value

    def set_tools(self):
        accelerators = Gtk.AccelGroup()
        window = self.get_toplevel()
        window.add_accel_group(accelerators)

        tools_shorcuts = ['a', 'p']
        for num, button in enumerate(self.get_children()):
            if num == 0:
                self.current_tool = self.tools[0]
            button.connect('toggled', self.on_button_toggled, num)
            key, mod = Gtk.accelerator_parse(tools_shorcuts[num])
            button.get_child().add_accelerator(
                'clicked', accelerators, key, mod, Gtk.AccelFlags.VISIBLE
            )

    def on_button_toggled(self, button, num):
        if button.get_active():
            self.current_tool = self.tools[num]
