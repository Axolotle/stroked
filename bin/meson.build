# Create configuration variables for Stroked's executable.
bin_conf = configuration_data()
bin_conf.set('app_rdnn', app_rdnn)
bin_conf.set('version', meson.project_version())
bin_conf.set('pkgdatadir', pkgdatadir)
bin_conf.set('localedir', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
bin_conf.set('pythondir', pythondir)

# Insert variables to Stroked's executable and install.
configure_file(
  input: 'stroked.in',
  output: 'stroked',
  configuration: bin_conf,
  install: true,
  install_dir: get_option('bindir')
)

# Add 'run' command to ninja to be able to run the app from '_build/' without real install.
stroked = join_paths(meson.build_root(), 'bin/stroked')
run_target('run', command: [stroked], depends: [stroked_resources])
