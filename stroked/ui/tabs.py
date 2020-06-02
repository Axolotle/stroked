from gi.repository import Gtk, GObject

from stroked.ui import Canvas


@Gtk.Template.from_resource('/space/autre/stroked/ui/tabs.ui')
class Tabs(Gtk.Notebook):
    __gtype_name__ = 'Tabs'

    __gsignals__ = {
        'current_glyph_changed': (
            GObject.SIGNAL_RUN_FIRST, None, (object, str))
    }

    def __init__(self):
        super().__init__()

    @property
    def active_tab(self):
        return self.get_nth_page(self.get_current_page())

    @property
    def active_canvas(self):
        index = self.get_current_page()
        if index == 0:
            return None
        return self.get_nth_page(index).get_children()[0]

    def add_tab(self, label_text):
        # Pack the canvas in a box to avoid context glitches
        tab = Gtk.Box()
        canvas = Canvas()
        tab.pack_start(canvas, True, True, 0)

        tab_label = Gtk.HBox(spacing=10)
        btn = Gtk.Button.new_from_icon_name('gtk-close', Gtk.IconSize.MENU)
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.connect('clicked', self.on_close_button_clicked, tab)
        tab_label.pack_start(Gtk.Label(label_text), True, True, 0)
        tab_label.pack_end(btn, False, False, 0)
        tab_label.show_all()

        index = self.append_page(tab, tab_label)
        self.show_all()
        return index

    def rename_tab(self, old_label_text, new_label_text):
        index = self.get_tab_index_from_label(old_label_text)
        if index is not None:
            tab = self.get_nth_page(index)
            label_widget = self.get_tab_label(tab).get_children()[0]
            label_widget.set_label(new_label_text)

    def open_tab(self, label_text):
        index = self.get_tab_index_from_label(label_text)
        if index is None:
            index = self.add_tab(label_text)
        self.set_current_page(index)

    def close_tab(self, index=None):
        if index is None:
            index = self.get_current_page()
        if index > 0:
            self.remove_page(index)

    def get_tab_label_text(self, tab):
        # Be careful, this is an overiding of the base `Notebook`'s method
        # `get_tab_label_text` since the label is actually a box with a label
        # and a button.
        return self.get_tab_label(tab).get_children()[0].get_label()

    def set_tab_label_text(self, tab, text):
        # Be careful, same as above method
        self.get_tab_label(tab).get_children()[0].set_label(text)

    def get_tab_index_from_widget(self, widget):
        for index in range(1, self.get_n_pages()):
            if widget == self.get_nth_page(index):
                return index
        return None

    def get_tab_index_from_label(self, text):
        for index in range(1, self.get_n_pages()):
            if text == self.get_tab_label_text(self.get_nth_page(index)):
                return index
        return None

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯
    # Methods defined with a decorator `@Gtk.Template.Callback` are defined in
    # the template's xml ui file.

    @Gtk.Template.Callback('on_page_switched')
    def _on_page_switched(self, tabs, tab, index):
        # FIXME, tool need to be reset even if the next tab is the glyphlist
        # try to do that in another scope.
        self.get_toplevel().toolbar.current_tool.reset()
        if index > 0:
            glyph_name = self.get_tab_label_text(tab)
            canvas = tab.get_children()[0]
            self.emit('current_glyph_changed', canvas, glyph_name)

    def on_close_button_clicked(self, button, tab):
        index = self.get_tab_index_from_widget(tab)
        self.close_tab(index)
