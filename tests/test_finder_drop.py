#!/usr/bin/python3
# Run inside the image with a display (xvfb-run) and a D-Bus session: python3 tests/test_finder_drop.py
# Drop handling of Mango Finder, driven directly (synthetic mouse drags do not start
# GTK drags under Xvfb): same disk -> move; Ctrl -> copy; onto the Trash -> trash.
import os, runpy, shutil, time
ns = runpy.run_path("/usr/bin/mangos-finder", run_name="finder")
Gtk, GLib, Gio, Gdk = ns["Gtk"], ns["GLib"], ns["Gio"], ns["Gdk"]
Gtk.drag_finish = lambda *a: None
shutil.rmtree("/root/T5", ignore_errors=True); os.makedirs("/root/T5/Sub"); os.makedirs("/root/T5/Other")
for n in ("a.txt", "b.txt", "c.txt"):
    open(f"/root/T5/{n}", "w").write(n)
app = ns["App"](); app.register(None); ns["load_css"]()
w = ns["Finder"](app, "/root/T5"); w.show_all()
class Data:
    def __init__(self, uris): self.u = uris
    def get_uris(self): return self.u
def pump(sec):
    end = time.time() + sec
    while time.time() < end:
        Gtk.main_iteration_do(False); time.sleep(0.01)
print("window ready", flush=True); pump(1.5)
F = lambda p: Gio.File.new_for_path(p)
w.drop_files(None, Data([F("/root/T5/a.txt").get_uri()]), 0, F("/root/T5/Sub")); pump(1.5)
print("drop on folder (same disk) moves:", os.path.exists("/root/T5/Sub/a.txt") and not os.path.exists("/root/T5/a.txt"))
w.drop_files(None, Data([F("/root/T5/b.txt").get_uri()]), 0, "trash"); pump(1.5)
print("drop on Trash trashes:", not os.path.exists("/root/T5/b.txt"))
w.drop_files(None, Data([F("/root/T5/c.txt").get_uri()]), 0, F("/root/T5")); pump(1.0)
print("drop in its own folder does nothing:", os.path.exists("/root/T5/c.txt") and len(os.listdir("/root/T5")) == 3)
w.drop_files(None, Data([F("/root/T5/Sub").get_uri()]), 0, F("/root/T5/Sub")); pump(1.0)
print("drop a folder on itself does nothing:", os.path.isdir("/root/T5/Sub") and os.path.exists("/root/T5/Sub/a.txt"))
shutil.rmtree("/dev/shm/T5x", ignore_errors=True); os.makedirs("/dev/shm/T5x")
w.drop_files(None, Data([F("/root/T5/c.txt").get_uri()]), 0, F("/dev/shm/T5x")); pump(1.5)
print("drop on another disk copies:", os.path.exists("/dev/shm/T5x/c.txt") and os.path.exists("/root/T5/c.txt"))
w.act_undo(); pump(1.5)
print("undo removes the copy on the other disk, original kept:", not os.path.exists("/dev/shm/T5x/c.txt") and os.path.exists("/root/T5/c.txt"))
shutil.rmtree("/dev/shm/T5x", ignore_errors=True)
