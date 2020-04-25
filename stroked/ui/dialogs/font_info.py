from datetime import datetime

from gi.repository import Gtk


def set_widget_value(widget, value):



class DateEntry(Gtk.Entry, Gtk.Editable):
    __gtype_name__ = 'DateEntry'

    def __init__(self):
        super().__init__()

    def do_delete_text(self, start_pos, end_pos):
        pass

    def do_insert_text(self, new_text, length, position):
        text = self.get_text()
        new_text = text[:position] + new_text + text[position+1:]
        try:
            datetime.strptime(new_text, '%Y/%m/%d %H:%M:%S')
            self.get_buffer().set_text(new_text, len(new_text))
            Gtk.Entry.do_move_cursor(self, Gtk.MovementStep(0), 1, False)
            return position + length
        except ValueError:
            pass

        return position


@Gtk.Template.from_resource('/space/autre/stroked/ui/font_info_window.ui')
class WindowFontInfo(Gtk.Window):
    __gtype_name__ = 'WindowFontInfo'

    familyName = Gtk.Template.Child('family-name-entry')
    openTypeNameDesigner = Gtk.Template.Child('designer-entry')
    openTypeNameDesignerURL = Gtk.Template.Child('designer-url-entry')
    copyright = Gtk.Template.Child('copyright-entry')
    openTypeNameLicense = Gtk.Template.Child('license-entry')
    versionMajor = Gtk.Template.Child('version-major-spin-button')
    versionMinor = Gtk.Template.Child('version-minor-spin-button')
    openTypeHeadCreated = Gtk.Template.Child('date-entry')

    gridWidth = Gtk.Template.Child('grid-width-spin-button')
    gridHeight = Gtk.Template.Child('grid-height-spin-button')

    def __init__(self, window):
        super().__init__(title='Font Info ' + window.filename,
                         transient_for=window)

        self.lib = window.font.lib
        self.info = window.font.info
        self.hydrate()

        for prop in self.__gtktemplate_widgets__.values():
            widget = getattr(self, prop)
            if 'version' in prop:
                widget.connect('value-changed', self.on_version_edited, prop)
            else:
                widget.connect('focus-out-event', self.on_edited, prop)

        self.versionMinor.connect('output', self.show_leading_zeros)

    def hydrate(self):
        info = self.info.getDataForSerialization()
        lib = self.lib
        for data in [info, lib]:
            for attr_name, value in data.items():
                if value and hasattr(self, attr_name):
                    widget = getattr(self, attr_name)
                    if isinstance(widget, Gtk.SpinButton):
                        widget.get_adjustment().set_value(value)
                    elif isinstance(widget, (Gtk.Entry, DateEntry)):
                        widget.set_text(value)

    def edit_info(self, prop, value):
        if value != getattr(self.info, prop):
            setattr(self.info, prop, value)

    def edit_lib(self, prop, value):
        if value != self.lib[prop]:
            self.lib[prop] = value

    def on_edited(self, widget, event, prop):
        if isinstance(widget, Gtk.SpinButton):
            value = int(widget.get_adjustment().get_value())
        elif isinstance(widget, Gtk.Entry):
            value = widget.get_text().strip()
            if value == '':
                value = None
        else:
            return

        if prop in self.info._properties:
            self.edit_info(prop, value)
        else:
            self.edit_lib(prop, value)

    def on_version_edited(self, widget, prop):
        major = int(self.versionMajor.get_adjustment().get_value())
        minor = int(self.versionMinor.get_adjustment().get_value())

        self.edit_info('versionMajor', major)
        self.edit_info('versionMinor', minor)
        self.edit_info('openTypeNameVersion',
                       'Version: {}.{:03d}'.format(major, minor))

    def show_leading_zeros(self, widget):
        value = int(widget.get_adjustment().get_value())
        widget.set_text('{:03d}'.format(value))
        return True
