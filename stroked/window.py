import os

from gi.repository import Gtk, Gdk, Gio

from stroked.ui import dialogs


@Gtk.Template.from_resource('/space/autre/stroked/ui/window.ui')
class StrokedWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'StrokedWindow'

    toolbar = Gtk.Template.Child('toolbar')
    tabs = Gtk.Template.Child('tabs')
    masters_store = Gtk.Template.Child('masters-store')
    masters_selection = Gtk.Template.Child('masters-selection')
    glyph_infos = Gtk.Template.Child('glyph-infos')

    def __init__(self, app, font, filename='Untitled', font_path=None):
        title = '{} - Stroked'.format(filename)
        super().__init__(application=app, title=title)

        self._set_window_actions()

        for z in self.props:
            print(z)

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

        self.current_glyph = None

    # ╭──────────────────────╮
    # │ WINDOW ACTIONS SETUP │
    # ╰──────────────────────╯

    def set_simple_action(self, name, handler=None, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect(
            'activate', getattr(self, 'on_' + name) if handler is None else handler
        )
        self.add_action(action)
        if shortcuts is not None:
            self.props.application.set_accels_for_action('win.' + name, shortcuts)

    def _set_window_actions(self):
        window_simple_actions = [
            # File
            ('save', ['<primary>s']),
            ('save_as', ['<primary><shift>s']),
            ('export', ['<primary>e']),
            ('close', ['<primary><shift>w']),
            # Font
            ('font_info', ['<primary>i']),
        ]

        for name, shortcuts in window_simple_actions:
            self.set_simple_action(name, shortcuts=shortcuts)

    # ╭─────────────────────────╮
    # │ WINDOW ACTIONS HANDLERS │
    # ╰─────────────────────────╯

    def on_save(self, *args):
        saved = False
        if self.path is None:
            saved = self.on_save_as()
        else:
            self.font.save(path=self.path)
            self.on_font_changed()
            saved = True
        return saved

    def on_save_as(self, *args):
        saved = False
        dialog = Gtk.FileChooserDialog(
            'Please choose a folder name',
            self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )
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
            self.font.save(path=path)
            self.filename = os.path.split(path)[-1]
            self.path = path
            self.on_font_changed()
            saved = True
        return saved

    def on_export(self, action, param):
        dialog = dialogs.DialogExport(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            options = dialog.get_options()
            options['masters'] = [self.font._layers[name]
                                  for name in options['masters']]
            self.font.export(options['path'], options['format'], options['masters'])
        dialog.destroy()

    @Gtk.Template.Callback('on_close')
    def on_close(self, *args):
        close = True
        if self.font.dirty:
            dialog = dialogs.DialogAskSave(self)
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                close = self.on_save()
            elif response == Gtk.ResponseType.CANCEL:
                close = False
        if close:
            self.destroy()
        return close

    def on_font_info(self, action, param):
        dialog = dialogs.WindowFontInfo(self)
        dialog.show()

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯
    # methods defined with a decorator `@Gtk.Template.Callback` are defined in
    # the template's xml ui file.

    @Gtk.Template.Callback('on_keypress')
    def _on_keypress(self, window, event):
        focused_widget = self.get_focus()
        if (
            isinstance(focused_widget, Gtk.Entry)
            and (not event.state or event.state & Gdk.ModifierType.MOD2_MASK)
            and event.keyval in [97, 112]
        ):
            # FIXME hacky way to not trigger tools accelerators
            focused_widget.do_key_press_event(focused_widget, event)
            return Gdk.EVENT_STOP
        if not event.state & Gdk.ModifierType.CONTROL_MASK:
            return
        key_name = Gdk.keyval_name(event.keyval)
        if key_name == 'w':
            self.tabs.close_tab()

    @Gtk.Template.Callback('on_master_select_changed')
    def _on_master_select_changed(self, selection):
        model, treeiter = selection.get_selected()
        self.font.active_master = model[treeiter][0]
        curr_canvas = self.tabs.active_canvas
        if curr_canvas is not None:
            curr_canvas._tool.reset()
            curr_canvas.glyph = self.font.active_master[curr_canvas.glyph.name]

    def on_current_glyph_changed(self, tabs, canvas, glyph_name):
        glyph = self.font.active_master[glyph_name]
        canvas._tool = self.toolbar.current_tool
        canvas.glyph = glyph
        self.glyph_infos.set_current_glyph(glyph)
        self.current_glyph = glyph

    def on_current_tool_changed(self, widget, tool):
        curr_canvas = self.tabs.active_canvas
        if curr_canvas is not None:
            # Reset previous tool
            curr_canvas._tool.reset()
            curr_canvas._tool = tool

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
