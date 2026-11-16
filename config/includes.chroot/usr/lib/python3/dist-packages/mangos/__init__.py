"""Shared helpers for the small MangOS desktop tools."""
import locale, os

def is_italian():
    lang = os.environ.get("LANGUAGE") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or ""
    return lang.startswith("it")

def tr(en, it):
    """Tiny two-language translation helper (English default, Italian)."""
    return it if is_italian() else en

def read(path, default=""):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return default

def os_release():
    data = {}
    for line in read("/etc/os-release").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k] = v.strip('"')
    return data

CSS = b"""
.mangos-title { font-family: Inter; font-size: 26px; font-weight: 700; }
.mangos-subtitle { font-size: 13px; opacity: .65; }
.mangos-key { font-weight: 600; }
.mangos-value { opacity: .8; }
.mangos-card { border-radius: 14px; padding: 10px; border: 2px solid alpha(currentColor, .12); }
.mangos-card.selected { border-color: #0A84FF; }
button.suggested-action { background: #0A84FF; color: white; border-radius: 7px; padding: 4px 18px; border: none; }
"""

def load_css():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk
    p = Gtk.CssProvider(); p.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), p,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
