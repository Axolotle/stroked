#!/usr/bin/env python3

import os
from subprocess import call

# TODO: try to find a way to execute this command only when `run` (not on `install`)
# This script will compile schemas and translations and make them available in local run.

source_dir = os.environ.get('MESON_SOURCE_ROOT')
build_datadir = os.path.join(os.environ.get('MESON_BUILD_ROOT'), 'data')
source_datadir = os.path.join(source_dir, 'data')

print('Install schemas in build dir...')
call(['glib-compile-schemas', source_datadir])
call(['mkdir', '-p', os.path.join(build_datadir, 'glib-2.0', 'schemas')])
call([
    'mv',
    os.path.join(source_datadir, 'gschemas.compiled'),
    os.path.join(build_datadir, 'glib-2.0', 'schemas')
])

print('Compiling translations in build dir...')
# Add to set this variable to nothing to avoid meson error.
os.environ['MESON_INSTALL_PREFIX'] = ''
# Just copied the command that ninja runs when compiling locales, seems to work.
call([
    'meson',
    '--internal',
    'gettext',
    'install',
    '--subdir=' + os.path.join(source_dir, 'po'),
    '--localedir=' + os.path.join(build_datadir, 'locale'),
    '--pkgname=stroked'
])
