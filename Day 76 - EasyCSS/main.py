import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_margin_top(10)
    box.set_margin_bottom(10)
    box.set_margin_start(10)
    box.set_margin_end(10)

    button_class_name_label = Gtk.Label(label="Button class name for CSS")
    box.append(button_class_name_label)

    button_class_name = Gtk.Entry()
    button_class_name.set_text("")
    box.append(button_class_name)

    spacer = Gtk.Label(label="")
    box.append(spacer)

    btn = Gtk.Button(label="Save")
    btn.connect('clicked', save_now)
    box.append(btn)

    win.set_child(box)
    win.present()


def save_now(_args):
    print('Definitively not saved')


app = Gtk.Application(application_id='antoine.meloche.EasyCSS')
app.connect('activate', on_activate)
app.run(None)
