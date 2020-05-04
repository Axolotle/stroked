from gi.repository import Gtk, GObject

from stroked.tools import SelectTool, PenTool


class Toolbar(Gtk.Toolbar):
    __gtype_name__ = 'Toolbar'

    __gsignals__ = {
        'current_tool_changed': (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self):
        super().__init__()

        self._current_tool = 0
        self.tools = [
            SelectTool(),
            PenTool()
        ]

    def do_realize(self):
        Gtk.Toolbar.do_realize(self)
        self.set_tools()

    @property
    def current_tool(self):
        return self.tools[self._current_tool]

    def set_tools(self):
        accelerators = Gtk.AccelGroup()
        window = self.get_toplevel()
        window.add_accel_group(accelerators)

        tools_shorcuts = ['a', 'p']
        for num, button in enumerate(self.get_children()):
            button.connect('toggled', self.on_button_toggled, num)
            key, mod = Gtk.accelerator_parse(tools_shorcuts[num])
            button.get_child().add_accelerator(
                'clicked', accelerators, key, mod, Gtk.AccelFlags.VISIBLE
            )

    def on_button_toggled(self, button, num):
        if button.get_active():
            self._current_tool = num
            self.emit('current_tool_changed', self.tools[num])
