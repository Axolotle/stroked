datadir = join_paths(get_option('prefix'), get_option('datadir'))


# ╭─────────────────╮
# │ .GRESOURCE.XML  │
# ╰─────────────────╯

# Compile resources and install
stroked_resources = gnome.compile_resources(
  app_rdnn,
  app_rdnn + '.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir
)


# ╭───────────────╮
# │ .GSCHEMA.XML  │
# ╰───────────────╯

# Install schema file
install_data(
  app_rdnn + '.gschema.xml',
  install_dir: 'share/glib-2.0/schemas'
)

# Validate schemas
compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

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
  install_dir: join_paths(datadir, 'applications')
)

# Validate desktop file
desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [stroked_desktop])
endif


# ╭──────────────╮
# │ .APPDATA.XML │
# ╰──────────────╯

# Create configuration variables for Stroked's appdata.
appdata_conf = configuration_data()
appdata_conf.set('app_rdnn', app_rdnn)

# Insert variables and translate Stroked's appdata
stroked_appdata = i18n.merge_file(
  'appdata',
  input: configure_file(
    input: app_rdnn + '.appdata.xml.in.in',
    output: app_rdnn + '.appdata.xml.in',
    configuration: appdata_conf
  ),
  output: app_rdnn + '.appdata.xml',
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(datadir, 'metainfo')
)

# Validate the appdata file
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test (
    'Validate appdata file',
    appstream_util,
    args: ['validate-relax', stroked_appdata]
  )
endif


# ╭───────╮
# │ ICONS │
# ╰───────╯

# Install icon
install_data(
    app_rdnn + '.svg',
    install_dir: join_paths(datadir, 'icons/hicolor/scalable/apps')
)
