prefix = get_option('prefix')

cdata = configuration_data()
cdata.set('VERSION', meson.project_version())
cdata.set('pkgdatadir', join_paths(prefix, pkgdatadir))
cdata.set('localedir', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))

configure_file(
  input: 'stroked.in',
  output: 'stroked',
  configuration: cdata,
  install: true,
  install_dir: get_option('bindir')
)

stroked = join_paths(meson.build_root(), 'bin/stroked')
run_target('run',
  command: [stroked],
  depends: [
    stroked_resources
  ]
)
