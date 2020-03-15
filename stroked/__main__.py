import sys
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from stroked.app import Stroked


app = Stroked()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
