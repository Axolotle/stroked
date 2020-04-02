from os.path import join, abspath, dirname

from gi.repository import Gio


Gio.resources_register(Gio.Resource.load(
    join(abspath(dirname(__file__)), 'data/stroked.gresource')
))
