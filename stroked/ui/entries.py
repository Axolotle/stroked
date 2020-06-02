from gi.repository import Gtk, Gdk, GObject


_INVALID_COLOR = Gdk.Color(65535, 0, 0)


class CustomEntry(Gtk.Entry, Gtk.Editable):
    __gtype_name__ = 'CustomEntry'

    def __init__(self):
        super().__init__()
        self.connect('activate', self.check_if_safe_value)
        self.connect('focus_out_event', self.check_if_safe_value)

    def check_if_safe_value(self, entry, event=None):
        value = self.get_value()
        if value is not None:
            self.emit('safe_value_changed', value)
            self.modify_bg(Gtk.StateFlags.NORMAL, None)
        else:
            self.modify_bg(Gtk.StateFlags.NORMAL, _INVALID_COLOR)


class TextEntry(CustomEntry, Gtk.Entry, Gtk.Editable):
    __gtype_name__ = 'TextEntry'

    __gsignals__ = {
        'safe_value_changed': (GObject.SIGNAL_RUN_FIRST, None, (str, ))
    }

    def check_if_safe_value(self, entry, event=None):
        self.emit('safe_value_changed', self.get_text())

    def get_value(self, value=None):
        return value or self.get_text()

    def set_value(self, value):
        self.set_text(value)


class FloatEntry(CustomEntry, Gtk.Entry, Gtk.Editable):
    __gtype_name__ = 'FloatEntry'

    __gsignals__ = {
        'safe_value_changed': (GObject.SIGNAL_RUN_FIRST, None, (float, ))
    }

    def do_insert_text(self, new_text, length, pos):
        text = self.get_text()
        parsed_value = self.get_value(text[0:pos] + new_text + text[pos:])

        if parsed_value is None:
            return pos
        else:
            self.get_buffer().insert_text(pos, new_text, length)
            return pos + length

    def get_value(self, value=None):
        try:
            return float(value or self.get_text())
        except ValueError:
            return None

    def set_value(self, value):
        self.set_text(str(value))


class HexEntry(CustomEntry, Gtk.Entry, Gtk.Editable):
    __gtype_name__ = 'HexEntry'

    __gsignals__ = {
        'safe_value_changed': (GObject.SIGNAL_RUN_FIRST, None, (object, ))
    }

    def get_value(self, values=None):
        if values is None:
            values = self.get_text()
        try:
            return [int(value, 16) for value in values.split(' ')]
        except ValueError:
            return None

    def set_value(self, values):
        self.set_text(' '.join(
            [hex(value) for value in values]
        ).replace('x', '0').upper())
