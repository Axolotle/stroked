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

        self.tabs.connect(
            'current_glyph_changed', self.on_current_glyph_changed)
        self.toolbar.connect(
            'current_tool_changed', self.on_current_tool_changed)

        self.font = font
        self.filename = filename
        self.path = font_path

        for layer in font._layers:
            self.masters_store.append([layer.name])
        self.masters_selection.select_iter(self.masters_store.get_iter_first())

        self.font.addObserver(self, 'on_font_changed', 'Font.Changed')
        self.font.layers.addObserver(
            self, 'on_master_added', 'LayerSet.LayerAdded')
        self.font.layers.addObserver(
            self, 'on_master_deleted', 'LayerSet.LayerDeleted')
        self.font.layers.addObserver(
            self, 'on_master_renamed', 'LayerSet.LayerNameChanged')

    def set_actions(self, app):
        actions = [
            ['font_info', ['<primary>i']],
            ['export', ['<primary>e']],
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

    def on_export(self, action, param):
        dialog = dialogs.DialogExport(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.font.export(*dialog.get_options())
        dialog.destroy()

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

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

    @Gtk.Template.Callback('on_master_select_changed')
    def _on_master_select_changed(self, selection):
        model, treeiter = selection.get_selected()
        self.font.active_master = model[treeiter][0]
        active_tab = self.tabs.active_tab
        if isinstance(active_tab, Canvas):
            active_tab._tool.reset(active_tab)
            active_tab.glyph = self.font.active_master[active_tab.glyph.name]

    def on_current_glyph_changed(self, tabs, canvas, glyph_name):
        canvas._tool = self.toolbar.current_tool
        canvas.glyph = self.font.active_master[glyph_name]

    def on_current_tool_changed(self, widget, tool):
        current_canvas = self.tabs.active_tab
        current_canvas._tool.reset(current_canvas)
        current_canvas._tool = tool

    # ╭────────────────────────╮
    # │ DEFCON EVENTS HANDLERS │
    # ╰────────────────────────╯

    def on_font_changed(self, notification=None):
        title = self.get_title()
        dirty = '*' if self.font.dirty else ''
        supposed_title = '{}{} - Stroked'.format(dirty, self.filename)
        if title != supposed_title:
            self.set_title(supposed_title)

    def on_master_added(self, notification):
        master_name = notification.data['name']
        self.masters_store.append([master_name])

    def on_master_deleted(self, notification):
        master_name = notification.data['name']
        for row in self.masters_store:
            if row[0] == master_name:
                self.masters_store.remove(row.iter)

    def on_master_renamed(self, notification):
        data = notification.data
        old_name = data["oldName"]
        new_name = data["newName"]
        for row in self.masters_store:
            if row[0] == old_name:
                row[0] = new_name
