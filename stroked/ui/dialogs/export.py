import os

from gi.repository import Gtk


@Gtk.Template.from_resource('/space/autre/stroked/ui/export_dialog.ui')
class DialogExport(Gtk.Dialog):
    __gtype_name__ = 'DialogExport'

    notebook = Gtk.Template.Child('export-notebook')

    # Common elements
    masters_list = Gtk.Template.Child('masters-list')

    # OTF panel
    ttf_checkbox = Gtk.Template.Child('ttf-checkbox')
    otf_destination = Gtk.Template.Child('otf-destination')

    # UFO panel
    ufo_destination = Gtk.Template.Child('ufo-destination')

    def __init__(self, window):
        super().__init__(title='Export ' + window.filename,
                         transient_for=window)

        masters = window.font.masters
        for master in masters:
            row = Gtk.ListBoxRow()
            row.set_can_focus(False)
            checkbox = Gtk.CheckButton.new_with_label(master.name.split('.')[-1])
            checkbox.set_active(True)
            row.add(checkbox)
            self.masters_list.add(row)
        self.masters_list.show_all()

        self.otf_destination.set_current_folder(
            os.path.expanduser('~/.local/share/fonts/'))
        current_path = os.path.dirname(window.path) if window.path else None
        self.ufo_destination.set_current_folder(
            current_path or os.path.expanduser('~'))

    @property
    def active_tab(self):
        notebook = self.notebook
        return notebook.get_nth_page(notebook.get_current_page())

    def get_options(self):
        notebook = self.notebook
        tab = self.active_tab
        format = notebook.get_tab_label_text(tab)
        return format, getattr(self, 'parse_options_' + format)()

    def parse_options_otf(self):
        return {
            'masters': self.get_selected_masters(),
            'ttf': self.ttf_checkbox.get_active(),
            'path': self.otf_destination.get_filename(),
        }

    def parse_options_ufo(self):
        path = self.ufo_destination.get_filename()
        if path is None:
            raise ValueError('Destination is None')
        return {
            'masters': self.get_selected_masters(),
            'folder': path,
        }

    def get_selected_masters(self):
        names = []
        for row in self.masters_list.get_children():
            checkbox = row.get_child()
            if checkbox.get_active():
                names.append(checkbox.get_label())
        return names

    @Gtk.Template.Callback('on_delete')
    def _on_delete(self, dialog, event):
        self.response(Gtk.ResponseType.CANCEL)

    @Gtk.Template.Callback('on_page_switch')
    def _on_page_switch(self, tabs, tab, num):
        if num > 1:
            return
        list = self.masters_list
        next_container = tab.get_children()[0].get_children()[1]
        prev_container = list.get_parent()
        prev_container.remove(list)
        next_container.add(list)
