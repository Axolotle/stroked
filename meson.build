project(
  'stroked',
  version: '0.1.0',
  meson_version: '>= 0.50.0',
)

python = import('python')
gnome = import('gnome')
i18n = import('i18n')
# Find python3.
py_installation = python.find_installation('python3')
# Make sure Python is installed and found
if not py_installation.found()
    error('No valid python3 binary found')
endif
# Check dependencies.
dependency('gtk+-3.0', version: '>= 3.24.7')
dependency('pygobject-3.0', version: '>= 3.36.1')
# TODO: add other python packages ?

# Constants
app_rdnn = 'space.autre.stroked'
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
pythondir = py_installation.get_install_dir()

# Install Stroked's source code into local `site-packages` folder.
install_subdir('stroked', install_dir: pythondir)

# Those subdirs are handled by by their own `meson.build`.
subdir('data')
subdir('bin')
subdir('po')

meson.add_postconf_script('build_aux/meson_post_conf.py')
meson.add_install_script('build_aux/meson_post_install.py')
