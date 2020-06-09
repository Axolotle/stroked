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
