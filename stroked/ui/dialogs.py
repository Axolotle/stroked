import os.path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class DialogSaveBeforeQuit(Gtk.Dialog):

    def __init__(self, window):
        title = 'Close ' + window.filename
        Gtk.Dialog.__init__(self, title, window, 0,
            (Gtk.STOCK_CLOSE, Gtk.ResponseType.NO,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.YES
            ))

        self.set_default_size(150, 100)
        self.set_default_response(Gtk.ResponseType.YES)

        primary_label = Gtk.Label()
        primary_label.set_markup(
            '<big>Save changes to the <i>"{}"</i> font before closing?</big>\n'.format(window.filename))
        secondary_label = Gtk.Label('If you close without saving, your changes will be lost.')

        box = self.get_content_area()
        box.add(primary_label)
        box.add(secondary_label)
        box.show_all()

        self.connect('delete-event', self.on_delete)

    def on_delete(self, dialog, event):
        self.response(Gtk.ResponseType.CANCEL)
