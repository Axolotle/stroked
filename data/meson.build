# ╭─────────────────╮
# │ .GRESOURCES.XML │
# ╰─────────────────╯

# Compile resources and install
stroked_resources = gnome.compile_resources(
  app_rdnn,
  app_rdnn + '.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir
)

# ╭──────────╮
# │ .DESKTOP │
# ╰──────────╯

# Translate desktop file and install
stroked_desktop = i18n.merge_file(
  input: app_rdnn + '.desktop.in',
  output: app_rdnn + '.desktop',
  type: 'desktop',
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)

# Validate desktop file
desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [stroked_desktop])
endif
