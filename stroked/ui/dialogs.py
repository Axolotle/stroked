from gi.repository import Gtk


@Gtk.Template.from_resource('/space/autre/stroked/ui/simple_dialogs.ui')
class DialogAskSave(Gtk.Dialog):
    __gtype_name__ = 'DialogAskSave'

    label = Gtk.Template.Child('label')

    def __init__(self, window):
        super().__init__(title='Close ' + window.filename,
                         transient_for=window)

        self.label.set_label(self.label.get_label().format(window.filename))

    @Gtk.Template.Callback('on_delete')
    def _on_delete(self, dialog, event):
        self.response(Gtk.ResponseType.CANCEL)
