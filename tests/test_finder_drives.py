#!/usr/bin/python3
"""Mango Finder: USB sticks and drives (automount, open a window, preferences),
the D-Bus helpers' path handling. Uses stand-in volumes (no real drive needed).
Run inside the image with a display:  xvfb-run dbus-run-session -- python3 tests/test_finder_drives.py"""
import importlib.machinery, importlib.util, json, os, sys, tempfile
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp()
loader = importlib.machinery.SourceFileLoader("finder", "/usr/bin/mangos-finder")
spec = importlib.util.spec_from_loader("finder", loader); fd = importlib.util.module_from_spec(spec); loader.exec_module(fd)
from gi.repository import Gio, GLib
results = []


def check(name, cond, detail=""):
    results.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail and not cond else ""))


class FakeMount:
    def __init__(self, root, vol=None):
        self.root, self.vol = root, vol
    def get_default_location(self): return Gio.File.new_for_uri(self.root)
    def get_root(self): return Gio.File.new_for_uri(self.root)
    def get_volume(self): return self.vol


class FakeVolume:
    def __init__(self, name, auto=True, can=True):
        self.name, self.auto, self.can, self.mount_obj, self.mounted_calls = name, auto, can, None, 0
    def should_automount(self): return self.auto
    def can_mount(self): return self.can
    def get_mount(self): return self.mount_obj
    def get_uuid(self): return "uuid-" + self.name
    def get_name(self): return self.name
    def mount(self, flags, op, canc, cb):
        self.mounted_calls += 1
        self.mount_obj = FakeMount("file:///media/" + self.name, self)
        cb(self, None)
    def mount_finish(self, res): return True


app = fd.App()
opened = []
app.new_window = lambda where: opened.append(where.get_uri() if hasattr(where, "get_uri") else where)
app.automounting = set()

v = FakeVolume("CHIAVETTA")
app.on_volume_added(None, v)
check("USB stick is mounted when connected", v.mounted_calls == 1)
check("a window shows its files", opened == ["file:///media/CHIAVETTA"], opened)
app.on_mount_added(None, v.mount_obj)
check("no second window for the same stick", len(opened) == 1, opened)

opened.clear()
v2 = FakeVolume("INTERNO", auto=False)
app.on_volume_added(None, v2)
check("internal disks (no automount hint) are left alone", v2.mounted_calls == 0 and not opened)

fd.save_cfg({"autoopen": False}, fd.PREF_KEYS)
v3 = FakeVolume("FOTO")
app.on_volume_added(None, v3)
check("'show a window' off: mounted, no window", v3.mounted_calls == 1 and not opened, opened)

fd.save_cfg({"automount": False, "autoopen": True}, fd.PREF_KEYS)
v4 = FakeVolume("DISCO")
app.on_volume_added(None, v4)
check("'open automatically' off: nothing happens", v4.mounted_calls == 0 and not opened)

fd.save_cfg({"automount": True, "autoopen": True}, fd.PREF_KEYS)
app.on_mount_added(None, FakeMount("mtp://Google_Pixel/"))
check("a phone (MTP) opens a window", opened == ["mtp://Google_Pixel/"], opened)

# preferences and window settings do not overwrite each other
fd.save_cfg({"view": "list", "automount": False}, fd.WINDOW_KEYS)
c = fd.load_cfg()
check("window settings keep the preferences", c["view"] == "list" and c["automount"] is True, c)

# paths from the desktop (D-Bus): absolute, relative to a folder, URIs
check("to_file absolute", fd.to_file("/tmp/a b.txt").get_path() == "/tmp/a b.txt")
check("to_file relative to the working folder", fd.to_file("x.txt", "/home/u/Desktop").get_path() == "/home/u/Desktop/x.txt")
check("to_file URI", fd.to_file("file:///tmp/c%20d.txt").get_path() == "/tmp/c d.txt")
check("to_file trash", fd.to_file("trash:///").get_uri_scheme() == "trash")

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
