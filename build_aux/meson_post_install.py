#!/usr/bin/env python3

# from compileall import compile_dir
import os
from subprocess import call

# Run the extra compilations/updates needed by the system.
if 'DESTDIR' not in os.environ:
    prefix = os.environ.get('MESON_INSTALL_PREFIX', '/usr/local')
    datadir = os.path.join(prefix, 'share')

    print('Updating icon cache…')
    call(['gtk-update-icon-cache', '-tf', os.path.join(datadir, 'icons', 'hicolor')])
    print('Compiling GSettings schemas...')
    call(['glib-compile-schemas', os.path.join(datadir, 'glib-2.0', 'schemas')])
    print("Updating desktop database")
    call(["update-desktop-database", os.path.join(datadir, 'applications')])

    # print('Compiling python bytecode...')
    # compile_dir(destdir + path.join(pkgdatadir, 'stroked', 'stroked'), optimize=2)
