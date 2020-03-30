import gi
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gio
from gi.repository import Gtk

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
            ['quit', ['<primary>q']]
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

    def on_delete(self):
        pass


if __name__ == '__main__':
    import sys

    app = Stroked()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
