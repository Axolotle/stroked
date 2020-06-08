project('stroked',
  version: '0.1.0',
  meson_version: '>= 0.49.2',
)

python = import('python')
# Module objects
py_installation = python.find_installation('python3')
# Make sure Python is installed and found
if not py_installation.found()
    error('No valid python3 binary found')
endif

dependency('gtk+-3.0', version: '>= 3.24.7')
dependency('pygobject-3.0', version: '>= 3.36.1')

pkgdatadir = join_paths(get_option('datadir'), meson.project_name())

install_subdir(
    'stroked',
    exclude_directories: [
        '__pycache__',
        'font/__pycache__',
        'pens/__pycache__',
        'tools/__pycache__',
        'ui/__pycache__',
        'ui/dialogs/__pycache__',
        'ui/panels/__pycache__'
    ],
    install_dir: pkgdatadir
)
subdir('data')
subdir('bin')
