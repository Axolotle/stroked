gnome = import('gnome')

stroked_resources = gnome.compile_resources('stroked',
  'space.autre.stroked.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir
)

stroked_desktop = configure_file(
  input: 'space.autre.stroked.desktop',
  output: 'space.autre.stroked.desktop',
  copy: true,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [stroked_desktop]
  )
endif

gtk_builder_tool = find_program('gtk-builder-tool', required: false)
if gtk_builder_tool.found()
  ui_files = [
    ['ui', 'export_dialog.ui'],
    ['ui', 'font_info_window.ui'],
    ['ui', 'glyph_item.ui'],
    ['ui', 'glyph_list.ui'],
    ['ui', 'instance_stack_item.ui'],
    ['ui', 'menubar.ui'],
    ['ui', 'panels.ui'],
    ['ui', 'simple_dialogs.ui'],
    ['ui', 'tabs.ui'],
    ['ui', 'window.ui'],
  ]
  foreach ui_file : ui_files
    test('Validate @0@'.format(ui_file[1]), gtk_builder_tool,
      args: ['validate', join_paths(meson.current_source_dir(), ui_file[0], ui_file[1])]
    )
  endforeach
endif
