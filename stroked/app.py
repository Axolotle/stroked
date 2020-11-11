import os
import signal

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Gdk, GLib

from fontTools.ufoLib.errors import UFOLibError

from stroked.font import Font
from stroked.window import StrokedWindow


class Stroked(Gtk.Application):
    def __init__(self, version='', *args, **kwargs):
        super().__init__(
            *args,
            application_id='space.autre.stroked',
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        GLib.set_application_name('Stroked')
        GLib.set_prgname('space.autre.stroked')
        self._init_style()
        self._init_menubar()

        self.version = version
        self.settings = Gio.Settings.new('space.autre.stroked')

        # Command line arguments definitions
        self.add_main_option(
            'output',
            ord('o'),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            'Export destination',
            'FOLDER',
        )
        self.add_main_option(
            'format',
            ord('f'),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            'Export format, choose from [ufo, otf, tff]',
            'FORMAT',
        )

    def _init_style(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/space/autre/stroked/space.autre.stroked.css')
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _init_menubar(self):
        self.register(None)
        builder = Gtk.Builder.new_from_resource('/space/autre/stroked/ui/menubar.ui')
        self.set_menubar(builder.get_object('menu-bar'))

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # allow forced shutdown to quit silently
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self._set_app_actions()

    def do_activate(self):
        window = self.get_active_window()
        if window is None:
            self.on_new(None, None)

    def do_command_line(self, command_line):
        args = command_line.get_arguments()[1:]
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()
        if len(args) == 0:
            self.activate()
            if options:
                print('*Warning* Arguments ignored, missing file input.')
        else:
            path = args[0]
            try:
                font = Font(path=path)
            except UFOLibError:
                print('Invalid UFO folder for {}'.format(path))
                return 1
            if options:
                try:
                    dest_path = options['output']
                    format = options['format']
                except KeyError as err:
                    print('Missing argument: {}.'.format(err))
                    return 1
                try:
                    font.export(dest_path, format)
                except (OSError, ValueError) as err:
                    print(err)
                    return 1
            else:
                filename = os.path.split(path)[-1]
                window = StrokedWindow(self, font, filename, path)
                window.present()
        return 0

    # TODO: Move to Window ?
    def display_error(self, primary_msg, secondary_msg=None):
        window = self.get_active_window()
        dialog = Gtk.MessageDialog(
            window, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, primary_msg
        )
        if secondary_msg is not None:
            dialog.format_secondary_text(secondary_msg)
        dialog.run()
        dialog.destroy()

    # ╭───────────────────╮
    # │ APP ACTIONS SETUP │
    # ╰───────────────────╯

    def _set_app_actions(self):
        app_simple_actions = [
            ('new', ['<primary>n']),
            ('open', ['<primary>o']),
            ('quit', ['<primary>q']),
        ]

        for name, shortcuts in app_simple_actions:
            self.set_simple_action(name, shortcuts=shortcuts)

    def set_simple_action(self, name, handler=None, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect(
            'activate', getattr(self, 'on_' + name) if handler is None else handler
        )
        self.add_action(action)
        if shortcuts is not None:
            self.set_accels_for_action('app.' + name, shortcuts)

    # ╭──────────────────────╮
    # │ APP ACTIONS HANDLERS │
    # ╰──────────────────────╯

    def on_new(self, *args):
        font = Font()
        font.dirty = False
        window = StrokedWindow(self, font)
        window.present()

    def on_open(self, *args):
        window = self.props.active_window

        dialog = Gtk.FileChooserDialog(
            'Please choose an .ufo folder',
            window,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_modal(True)

        response = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()
        if response != Gtk.ResponseType.OK:
            return

        try:
            font = Font(path=path)
        except UFOLibError:
            dialog.destroy()
            self.display_error(
                'Invalid UFO folder',
                'Expected .ufo folder, got {}'.format(path)
            )
            return

        # Destroy the active window if it was an empty project.
        if not window.font.dirty and window.path is None:
            window.destroy()

        filename = os.path.split(path)[-1]
        window = StrokedWindow(self, font, filename, path)
        window.present()

    def on_quit(self, *args):
        for window in self.get_windows():
            closed = window.on_close()
            # Stop quitting if the user choosed to cancel.
            if not closed:
                return
        self.quit()


def main(version=''):
    import sys

    app = Stroked(version=version)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == '__main__':
    main()
