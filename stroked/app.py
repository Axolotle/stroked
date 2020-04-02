import os
import signal

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Gdk

from fontTools.ufoLib.errors import UFOLibError
from defcon import Font

import stroked.resources
from stroked.window import StrokedWindow


class Stroked(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='space.autre.stroked',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # allow forced shutdown to quit silently
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.set_actions()

    def do_activate(self):
        window = self.get_active_window()
        if window is None:
            self.on_new(None, None)

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

    def display_error(self, primary_msg, secondary_msg=None):
        window = self.get_active_window()
        dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.CANCEL, primary_msg)
        if secondary_msg is not None:
            dialog.format_secondary_text(secondary_msg)
        dialog.run()
        dialog.destroy()

    # ╭──────────────────────╮
    # │ GTK ACTIONS HANDLERS │
    # ╰──────────────────────╯

    def on_about(arg):
        pass

    def on_quit(self, action, param):
        for window in self.get_windows():
            keep_open = window.on_close()
            if keep_open:
                return
            else:
                window.destroy()
        self.quit()

    def on_new(self, action, param):
        font = Font()
        font.dirty = False
        window = StrokedWindow(self, font)
        window.present()

    def on_open(self, action, param):
        window = self.get_active_window()

        dialog = Gtk.FileChooserDialog('Please choose an .ufo folder', window,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_modal(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()

            try:
                font = Font(path=path)
            except UFOLibError as e:
                dialog.destroy()
                self.display_error(
                    'Invalid UFO folder',
                    'Expected .ufo folder, got {}'.format(path)
                )
                return

            if not window.font.dirty and window.path is None:
                window.destroy()

            filename = os.path.split(path)[-1]
            window = StrokedWindow(self, font, filename, path)
            window.present()

        dialog.destroy()

    def on_save(self, action=None, param=None):
        window = self.get_active_window()

        if window.path is None:
            return self.on_save_as()
        else:
            window.font.save(path=window.path)
            window.on_font_changed()
            return True

    def on_save_as(self, action=None, param=None):
        window = self.get_active_window()

        dialog = Gtk.FileChooserDialog('Please choose a folder name', window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name('untitled.ufo')
        dialog.set_modal(True)
        dialog.set_do_overwrite_confirmation(True)

        response = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            ext = os.path.splitext(path)[-1]
            if ext != '.ufo':
                path += '.ufo'
            window.font.save(path=path)
            window.filename = os.path.split(path)[-1]
            window.path = path
            window.on_font_changed()
            return True
        return False


    def on_delete(self):
        pass


def main():
    import sys

    app = Stroked()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == '__main__':
    main()
