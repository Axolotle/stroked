from datetime import date, datetime

from gi.repository import Gtk


def get_widget_value(widget):
    if isinstance(widget, DateEntry):
        value = widget.get_text() + ' 00:00:00'
    elif isinstance(widget, Gtk.Entry):
        value = widget.get_text().strip()
    elif isinstance(widget, Gtk.Adjustment):
        value = int(widget.get_value())

    if value != '':
        return value
    else:
        return None


def set_widget_value(widget, value):
    if isinstance(widget, DateEntry):
        widget.set_text(value.split(' ')[0])
    if isinstance(widget, Gtk.Entry):
        widget.set_text(value)
    else:
        widget.set_value(value)


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
            datetime.strptime(new_text, '%Y/%m/%d')
            self.get_buffer().set_text(new_text, len(new_text))
            Gtk.Entry.do_move_cursor(self, Gtk.MovementStep(0), 1, False)
            return position + length
        except ValueError:
            pass

        return position


@Gtk.Template.from_resource('/space/autre/stroked/ui/font_info_dialog.ui')
class DialogFontInfo(Gtk.Dialog):
    __gtype_name__ = 'DialogFontInfo'

    familyName = Gtk.Template.Child('family-name-entry')
    openTypeNameDesigner = Gtk.Template.Child('designer-entry')
    openTypeNameDesignerURL = Gtk.Template.Child('designer-url-entry')
    copyright = Gtk.Template.Child('copyright-entry')
    openTypeNameLicense = Gtk.Template.Child('license-entry')
    versionMajor = Gtk.Template.Child('version-major-number')
    versionMinor = Gtk.Template.Child('version-minor-number')
    openTypeHeadCreated = Gtk.Template.Child('date-entry')

    gridWidth = Gtk.Template.Child('grid-width-number')
    gridHeight = Gtk.Template.Child('grid-height-number')

    def __init__(self, window):
        super().__init__(title='Font Info ' + window.filename,
                         transient_for=window)
        self.lib = window.font.lib
        self.info = window.font.info
        self.hydrate()

    def hydrate(self):
        info = self.info.getDataForSerialization()
        lib = self.lib
        for data in [info, lib]:
            for attr_name, value in data.items():
                if value and hasattr(self, attr_name):
                    set_widget_value(getattr(self, attr_name), value)

        if 'openTypeHeadCreated' not in info:
            self.openTypeHeadCreated.set_text(
                '{:%Y/%m/%d}'.format(date.today()))

    def dehydrate(self):
        info = self.info.getDataForSerialization()
        lib = self.lib
        for id, attr_name in self.__gtktemplate_widgets__.items():
            data = info if attr_name in self.info._properties else lib
            value = get_widget_value(getattr(self, attr_name))
            if value is not None:
                data[attr_name] = value

        info['openTypeNameVersion'] = '{}.{:03d}'.format(
            info['versionMajor'], info['versionMinor']
        )

        return [info, lib]

    @Gtk.Template.Callback('on_delete')
    def _on_delete(self, dialog, event):
        self.response(Gtk.ResponseType.CANCEL)
