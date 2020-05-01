from gi.repository import Gtk, Gdk, Gio

from stroked.ui import dialogs, Canvas
import stroked.settings as stg


@Gtk.Template.from_resource('/space/autre/stroked/ui/window.ui')
class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    toolbar = Gtk.Template.Child('toolbar')
    tabs = Gtk.Template.Child('tabs')
    masters_store = Gtk.Template.Child('masters-store')
    masters_selection = Gtk.Template.Child('masters-selection')

    def __init__(self, app, font, filename='Untitled', font_path=None):
        title = '{} - Stroked'.format(filename)
        super().__init__(application=app, title=title)

        builder = Gtk.Builder.new_from_resource(
            '/space/autre/stroked/ui/menubar.ui')
        self.set_titlebar(builder.get_object('menubar'))

        self.set_actions(app)

        self.toolbar.connect('notify::current-tool', self.tabs.on_tool_changed)

        self.font = font
        self.filename = filename
        self.path = font_path
        self.font.addObserver(self, 'on_font_changed', 'Font.Changed')

        for layer in font._layers:
            self.masters_store.append([layer.name])
        self.masters_selection.select_iter(self.masters_store.get_iter_first())

    def set_actions(self, app):
        actions = [
            ['font_info', ['<primary>i']],
        ]

        for name, shortcuts in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect('activate', getattr(self, 'on_' + name))
            self.add_action(action)
            app.set_accels_for_action('win.' + name, shortcuts)

    # ╭──────────────────────╮
    # │ GTK ACTIONS HANDLERS │
    # ╰──────────────────────╯

    def on_font_info(self, action, param):
        dialog = dialogs.WindowFontInfo(self)
        dialog.show()

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

    @Gtk.Template.Callback('on_layer_select_changed')
    def _on_layer_select_changed(self, selection):
        model, treeiter = selection.get_selected()
        self.font.active_master = model[treeiter][0]
        active_tab = self.tabs.active_object
        if isinstance(active_tab, Canvas):
            active_tab.glyph = self.font.active_master[active_tab.glyph.name]
            active_tab.queue_draw()

    # ╭────────────────────────╮
    # │ DEFCON EVENTS HANDLERS │
    # ╰────────────────────────╯

    def on_font_changed(self, notification=None):
        title = self.get_title()
        dirty = '*' if self.font.dirty else ''
        supposed_title = '{}{} - Stroked'.format(dirty, self.filename)
        if title != supposed_title:
            self.set_title(supposed_title)
