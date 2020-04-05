from gi.repository import Gtk, Gdk

from stroked.ui import dialogs
import stroked.settings as stg


@Gtk.Template.from_resource('/space/autre/stroked/ui/window.ui')
class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    toolbar = Gtk.Template.Child('toolbar')
    tabs = Gtk.Template.Child('tabs')

    def __init__(self, app, font, filename='Untitled', font_path=None):
        title = '{} - Stroked'.format(filename)
        super().__init__(application=app, title=title)

        builder = Gtk.Builder.new_from_resource(
            '/space/autre/stroked/ui/menubar.ui')
        self.set_titlebar(builder.get_object('menubar'))

        self.toolbar.connect('notify::current-tool', self.tabs.on_tool_changed)

        self.font = font
        self.filename = filename
        self.path = font_path
        self.font.addObserver(self, 'on_font_changed', 'Font.Changed')

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    @Gtk.Template.Callback('on_linestyle_changed')
    def _on_linestyle_changed(self, elem):
        property_name = None
        property_value = None
        if isinstance(elem, Gtk.ComboBox):
            property_name = elem.get_name()
            if property_name in ['linecap', 'linejoin']:
                property_value = elem.get_active()
        elif isinstance(elem, Gtk.SpinButton):
            property_name = elem.get_name()
            property_value = elem.get_value()

        stg.set(['linestyle', property_name], property_value)
        self.tabs.update_tab_draw()

    @Gtk.Template.Callback('on_keypress')
    def _on_keypress(self, widget, event):
        if not event.state & Gdk.ModifierType.CONTROL_MASK:
            return
        key_name = Gdk.keyval_name(event.keyval)
        if key_name == 'w':
            self.tabs.close_tab()

    @Gtk.Template.Callback('on_close')
    def _on_close(self, window=None, event=None):
        stop_propagation = False
        if self.font.dirty:
            dialog = dialogs.DialogAskSave(self)
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                saved = self.get_application().on_save()
                stop_propagation = not saved
            elif response == Gtk.ResponseType.NO:
                stop_propagation = False
            elif response == Gtk.ResponseType.CANCEL:
                stop_propagation = True

        return stop_propagation

    # ╭────────────────────────╮
    # │ DEFCON EVENTS HANDLERS │
    # ╰────────────────────────╯

    def on_font_changed(self, notification=None):
        title = self.get_title()
        dirty = '*' if self.font.dirty else ''
        supposed_title = '{}{} - Stroked'.format(dirty, self.filename)
        if title != supposed_title:
            self.set_title(supposed_title)
