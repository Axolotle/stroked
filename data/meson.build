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

# Validating the appdata file
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test (
    'Validate appdata file',
    appstream_util,
    args: ['validate-relax', stroked_appdata]
  )
endif
