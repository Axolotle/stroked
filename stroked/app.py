import gi
import os
from defcon import Font
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

from stroked.window import StrokedWindow


class Stroked(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='space.autre.stroked',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.set_actions()

    def do_activate(self):
        if not self.window:
            self.window = StrokedWindow(self)

        self.window.present()

    def do_command_line(self, command_line):
        pass

    def set_actions(self):
        actions = [
            ['new', ['<primary>n']],
            ['open', ['<primary>o']],
            ['save', ['<primary>s']],
            ['save_as', ['<primary><shift>s']],
            ['quit', ['<primary>q']],
        ]

        for name, shortcuts in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect('activate', getattr(self, 'on_' + name))
            self.add_action(action)
            self.set_accels_for_action('app.' + name, shortcuts)

    def on_about(arg):
        pass

    def on_quit(self, action, param):
        self.quit()

    def on_new(self, action, param):
        pass

    def on_open(self, action, param):
        dialog = Gtk.FileChooserDialog('Please choose a folder', self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_modal(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.window.filename = dialog.get_filename()
            self.window.font = Font(path=self.window.filename)

        dialog.destroy()

    def on_save(self, action, param):
        if self.window.filename is None:
            self.on_save_as(action, param)
        else:
            self.window.font.save(path=self.window.filename)

    def on_save_as(self, action, param):
        dialog = Gtk.FileChooserDialog('Please choose a folder', self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name('untitled.ufo')
        dialog.set_modal(True)
        dialog.set_do_overwrite_confirmation(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.window.font.save(path=dialog.get_filename())

        dialog.destroy()

    def on_delete(self):
        pass


if __name__ == '__main__':
    import sys

    app = Stroked()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
