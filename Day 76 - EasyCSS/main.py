import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    btn = Gtk.Button(label="Save")
    btn.connect('clicked', save_now)
    win.set_child(btn)
    win.present()


def save_now(_args):
    print('Definitively not saved')


app = Gtk.Application(application_id='antoine.meloche.EasyCSS')
app.connect('activate', on_activate)
app.run(None)
