from datetime import datetime

from gi.repository import Gtk


class DateEntry(Gtk.Entry, Gtk.Editable):
    __gtype_name__ = 'DateEntry'

    def __init__(self):
        super().__init__()

    def do_delete_text(self, start_pos, end_pos):
        pass

    def do_insert_text(self, new_text, length, position):
        text = self.get_text()
        new_text = text[:position] + new_text + text[position+1:]
        try:
            datetime.strptime(new_text, '%Y/%m/%d %H:%M:%S')
            self.get_buffer().set_text(new_text, len(new_text))
            Gtk.Entry.do_move_cursor(self, Gtk.MovementStep(0), 1, False)
            return position + length
        except ValueError:
            pass

        return position


@Gtk.Template.from_resource('/space/autre/stroked/ui/font_info_window.ui')
class WindowFontInfo(Gtk.Window):
    __gtype_name__ = 'WindowFontInfo'

    familyName = Gtk.Template.Child('family-name-entry')
    openTypeNameDesigner = Gtk.Template.Child('designer-entry')
    openTypeNameDesignerURL = Gtk.Template.Child('designer-url-entry')
    copyright = Gtk.Template.Child('copyright-entry')
    openTypeNameLicense = Gtk.Template.Child('license-entry')
    versionMajor = Gtk.Template.Child('version-major-adj')
    versionMinor = Gtk.Template.Child('version-minor-adj')
    openTypeHeadCreated = Gtk.Template.Child('date-entry')

    gridWidth = Gtk.Template.Child('grid-width-adj')
    gridHeight = Gtk.Template.Child('grid-height-adj')

    v_minor_spin_button = Gtk.Template.Child('version-minor-spin-button')

    masters_stack = Gtk.Template.Child('masters-stack')

    instances_stack = Gtk.Template.Child('instances-stack')
    instances_stack_bar = Gtk.Template.Child('instances-stack-bar')

    master_delete_button = Gtk.Template.Child('master-delete-button')
    instance_delete_button = Gtk.Template.Child('instance-delete-button')

    def __init__(self, window):
        super().__init__(title='Font Info ' + window.filename,
                         transient_for=window)

        self.font = window.font
        self.lib = window.font.slib
        self.info = window.font.info
        self.hydrate()

        for prop in self.__gtktemplate_widgets__.values():
            widget = getattr(self, prop)
            if 'version' in prop:
                widget.connect('value-changed', self.on_version_edited, prop)
            elif (isinstance(widget, Gtk.Entry)
                  and not isinstance(widget, Gtk.SpinButton)):
                widget.connect('activate', self.on_edited, prop)
                widget.connect('focus-out-event', self.on_edited, prop)
            elif isinstance(widget, Gtk.Adjustment):
                widget.connect('value-changed', self.on_edited, prop)

        self.v_minor_spin_button.connect('output', self.show_leading_zeros)

    def hydrate(self):
        info = self.info.getDataForSerialization()
        lib = self.lib
        for data in [info, lib]:
            for attr_name, value in data.items():
                if value and hasattr(self, attr_name):
                    widget = getattr(self, attr_name)
                    if isinstance(widget, Gtk.Adjustment):
                        widget.set_value(value)
                    elif isinstance(widget, (Gtk.Entry, DateEntry)):
                        widget.set_text(value)

        for layer in self.font._layers:
            name = layer.name.split('.')[1]
            stack_item = StackItemMaster(name, layer.lib)
            self.masters_stack.add_titled(stack_item, name, name)

        for name, data in lib['instances'].items():
            stack_item = StackItemInstance(name, data, self.font)
            self.instances_stack.add_titled(stack_item, name, name)

        if len(self.masters_stack.get_children()) <= 1:
            self.master_delete_button.set_sensitive(False)
        if len(self.instances_stack.get_children()) <= 1:
            self.instance_delete_button.set_sensitive(False)

    def edit_info(self, prop, value):
        if value != getattr(self.info, prop):
            setattr(self.info, prop, value)

    def edit_lib(self, prop, value):
        if value != self.lib[prop]:
            self.lib[prop] = value

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_edited(self, widget, event, prop=None):
        if prop is None:
            prop = event
        if isinstance(widget, Gtk.Adjustment):
            value = int(widget.get_value())
        elif isinstance(widget, Gtk.Entry):
            value = widget.get_text().strip()
            if value == '':
                value = None
        else:
            return

        if prop in self.info._properties:
            self.edit_info(prop, value)
        else:
            self.edit_lib(prop, value)

    def on_version_edited(self, widget, prop):
        major = int(self.versionMajor.get_value())
        minor = int(self.versionMinor.get_value())

        self.edit_info('versionMajor', major)
        self.edit_info('versionMinor', minor)
        self.edit_info('openTypeNameVersion',
                       'Version: {}.{:03d}'.format(major, minor))

    def change_master_name(self, stack_item, name):
        stack = self.masters_stack
        old_name = stack.child_get_property(stack_item, 'title')
        self.font._layers['master.' + old_name].name = 'master.' + name
        stack.child_set_property(stack_item, 'name', name)
        stack.child_set_property(stack_item, 'title', name)

    def change_instance_name(self, stack_item, name):
        stack = self.instances_stack
        old_name = stack.child_get_property(stack_item, 'title')
        self.lib['instances'][name] = self.lib['instances'].pop(old_name)
        stack.child_set_property(stack_item, 'name', name)
        stack.child_set_property(stack_item, 'title', name)

    def show_leading_zeros(self, widget):
        value = int(widget.get_adjustment().get_value())
        widget.set_text('{:03d}'.format(value))
        return True

    @Gtk.Template.Callback('on_master_added')
    def _on_master_added(self, button):
        master = self.font.add_master()
        name = master.name.split('.')[1]
        stack_item = StackItemMaster(name, master.lib)
        stack = self.masters_stack
        stack.add_titled(stack_item, name, name)
        stack.set_visible_child(stack_item)
        if len(stack.get_children()) > 1:
            button.set_sensitive(True)

    @Gtk.Template.Callback('on_master_deleted')
    def _on_master_deleted(self, button):
        stack = self.masters_stack
        stack_item = stack.get_visible_child()
        name = stack.child_get_property(stack_item, 'title')
        stack.remove(stack_item)
        self.font.delete_master(name)
        if len(stack.get_children()) <= 1:
            button.set_sensitive(False)

    @Gtk.Template.Callback('on_instance_added')
    def _on_instance_added(self, button):
        instance_ = self.font.add_instance()
        name = instance_['style_name']
        stack_item = StackItemInstance(name, instance_, self.font)
        stack = self.instances_stack
        stack.add_titled(stack_item, name, name)
        stack.set_visible_child(stack_item)
        if len(stack.get_children()) > 1:
            button.set_sensitive(True)

    @Gtk.Template.Callback('on_instance_deleted')
    def _on_instance_deleted(self, button):
        stack = self.instances_stack
        stack_item = stack.get_visible_child()
        name = stack.child_get_property(stack_item, 'title')
        stack.remove(stack_item)
        self.font.delete_instance(name)
        if len(stack.get_children()) <= 1:
            button.set_sensitive(False)


@Gtk.Template.from_resource('/space/autre/stroked/ui/master_stack_item.ui')
class StackItemMaster(Gtk.Box):
    __gtype_name__ = 'StackItemMaster'

    name_entry = Gtk.Template.Child('name-entry')

    weight = Gtk.Template.Child('weight-combo')
    width = Gtk.Template.Child('width-combo')

    ascender = Gtk.Template.Child('ascender-adj')
    capHeight = Gtk.Template.Child('capHeight-adj')
    xHeight = Gtk.Template.Child('xHeight-adj')
    descender = Gtk.Template.Child('descender-adj')

    completion = Gtk.Template.Child('name-completion')

    def __init__(self, name, data):
        super().__init__()

        self.name = name
        self.data = data['space.autre.stroked']

        self.hydrate()

        for prop in self.__gtktemplate_widgets__.values():
            widget = getattr(self, prop)
            if isinstance(widget, Gtk.Adjustment):
                widget.connect('value-changed', self.on_changed, prop)
            elif isinstance(widget, Gtk.ComboBox):
                widget.connect('changed', self.on_changed, prop)

        self.name_entry.connect('activate', self.on_name_changed)
        self.name_entry.connect('focus-out-event', self.on_name_changed)

        self.completion.set_match_func(self.match_func)

    def hydrate(self):
        self.name_entry.set_text(self.name)
        for attr_name, value in self.data.items():
            if value and hasattr(self, attr_name):
                widget = getattr(self, attr_name)
                if isinstance(widget, Gtk.Adjustment):
                    widget.set_value(value)
                elif isinstance(widget, Gtk.ComboBox):
                    widget.set_active_id(str(value))

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_changed(self, widget, prop):
        if isinstance(widget, Gtk.Adjustment):
            value = int(widget.get_value())
        elif isinstance(widget, Gtk.ComboBox):
            value = int(widget.get_active_id())

        self.data[prop] = value

    def on_name_changed(self, entry, *args):
        name = entry.get_text()
        if name != self.name:
            self.name = name
            self.get_toplevel().change_master_name(self, name)

    def match_func(self, completion, model, iter):
        return True


@Gtk.Template.from_resource('/space/autre/stroked/ui/instance_stack_item.ui')
class StackItemInstance(Gtk.Box):
    __gtype_name__ = 'StackItemInstance'

    master = Gtk.Template.Child('master-combo')

    style_name = Gtk.Template.Child('stylename-entry')
    weight = Gtk.Template.Child('weight-combo')
    width = Gtk.Template.Child('width-combo')

    is_bold = Gtk.Template.Child('bold-checkbox')
    is_italic = Gtk.Template.Child('italic-checkbox')
    related_instance = Gtk.Template.Child('related-instance-combo')

    linewidth = Gtk.Template.Child('linewidth-adj')
    linejoin = Gtk.Template.Child('linejoin-combo')
    linecap = Gtk.Template.Child('linecap-combo')
    single_point = Gtk.Template.Child('single-point-combo')

    def __init__(self, name, data, font):
        super().__init__()

        self.name = name
        self.data = data

        for layer in font._layers:
            self.master.append(layer.name, layer.name)
        for name in font.slib['instances'].keys():
            self.related_instance.append(name, name)

        self.hydrate()

        for prop in self.__gtktemplate_widgets__.values():
            widget = getattr(self, prop)
            if isinstance(widget, Gtk.Adjustment):
                widget.connect('value-changed', self.on_changed, prop)
            elif isinstance(widget, Gtk.ComboBox):
                widget.connect('changed', self.on_changed, prop)
            elif isinstance(widget, Gtk.CheckButton):
                widget.connect('toggled', self.on_toggled, prop)

        self.style_name.connect('activate', self.on_name_changed)
        self.style_name.connect('focus-out-event', self.on_name_changed)

    def hydrate(self):
        self.style_name.set_text(self.name)
        for attr_name, value in self.data.items():
            if value and hasattr(self, attr_name):
                widget = getattr(self, attr_name)
                if isinstance(widget, Gtk.Adjustment):
                    widget.set_value(value)
                elif isinstance(widget, Gtk.ComboBox):
                    widget.set_active_id(str(value))
                elif isinstance(widget, Gtk.CheckButton):
                    widget.set_active(value)

    # ╭─────────────────────╮
    # │ GTK EVENTS HANDLERS │
    # ╰─────────────────────╯

    def on_changed(self, widget, prop):
        if isinstance(widget, Gtk.Adjustment):
            value = widget.get_value()
        elif isinstance(widget, Gtk.ComboBox):
            value = widget.get_active_id()
            if prop not in ['master', 'related_instance']:
                value = int(value)
        self.data[prop] = value

    def on_name_changed(self, entry, *args):
        name = entry.get_text()
        if name != self.style_name:
            self.style_name = name
            self.get_toplevel().change_instance_name(self, name)

    def on_toggled(self, check_button, prop):
        self.data[prop] = check_button.get_active()
