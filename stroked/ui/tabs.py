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
        return self.get_nth_page(self.get_current_page()).get_children()[0]

    def add_tab(self, title):
        # Pack the canvas in a box to avoid context glitches
        canvas = Canvas()
        container = Gtk.Box()
        container.pack_start(canvas, True, True, 0)
        box = Gtk.HBox(spacing=10)
        close_button = Gtk.Button.new_from_icon_name(
            'gtk-close', Gtk.IconSize.MENU)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.connect('clicked', self.on_tab_close, canvas)

        box.pack_start(Gtk.Label(title), True, True, 0)
        box.pack_end(close_button, False, False, 0)
        box.show_all()

        num = self.append_page(container, box)
        self.show_all()

        return num

    def close_tab(self, num=None):
        if num is None:
            num = self.get_current_page()
        if num > 0:
            self.remove_page(num)

    def update_tab_draw(self, num=None):
        if num is None:
            num = self.get_current_page()
        if num > 0:
            self.get_nth_page(num).queue_draw()

    def find_num_from_tab_object(self, tab_object):
        for num in range(1, self.get_n_pages()):
            tab = self.get_nth_page(num)
            if tab == tab_object:
                return num
        return None

    def find_num_from_tab_label(self, label):
        for num in range(1, self.get_n_pages()):
            tab = self.get_nth_page(num)
            tab_label = self.get_tab_label(tab).get_children()[0].get_label()
            if label == tab_label:
                return num
        return None

    def on_tab_close(self, button, tab):
        num = self.find_num_from_tab_object(tab)
        if num is not None:
            self.close_tab(num)

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    @Gtk.Template.Callback('on_page_switched')
    def _on_page_switched(self, tabs, tab, num):
        prev_tab = self.active_tab
        if isinstance(prev_tab, Canvas):
            prev_tab._tool.reset(prev_tab)
        if num > 0:
            glyph_name = self.get_tab_label(tab).get_children()[0].get_label()
            self.emit('current_glyph_changed',
                      tab.get_children()[0], glyph_name)
