from gi.repository import Gtk

from stroked.ui import Canvas


@Gtk.Template.from_resource('/space/autre/stroked/ui/tabs.ui')
class Tabs(Gtk.Notebook):
    __gtype_name__ = 'Tabs'

    def __init__(self):
        super().__init__()
        self.current_tool = None

    @property
    def active_object(self):
        return self.get_nth_page(self.get_current_page())

    def add_tab(self, title, glyph):
        canvas = Canvas(glyph)
        box = Gtk.HBox(spacing=10)
        close_button = Gtk.Button.new_from_icon_name(
            'gtk-close', Gtk.IconSize.MENU)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.connect('clicked', self.on_tab_close, canvas)

        box.pack_start(Gtk.Label(title), True, True, 0)
        box.pack_end(close_button, False, False, 0)
        box.show_all()

        num = self.append_page(canvas, box)
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

    def find_num_from_tab_object(self, tab):
        for num in range(1, self.get_n_pages()):
            page = self.get_nth_page(num)
            if page == tab:
                return num
        return None

    def find_num_from_tab_label(self, label):
        for num in range(1, self.get_n_pages()):
            page = self.get_nth_page(num)
            page_label = self.get_tab_label(page).get_children()[0].get_label()
            if label == page_label:
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
        if num > 0:
            self.current_tool.set_canvas(tab)

    # ╭────────────╮
    # │ GTK NOTIFY │
    # ╰────────────╯

    def on_tool_changed(self, toolbar, param):
        self.current_tool = toolbar.get_property(param.name)
        canvas = self.active_object
        if isinstance(canvas, Canvas):
            self.current_tool.set_canvas(canvas)
