"""How heavy an app is, and whether it can run on this Mac (Mango Store labels).

weight(key, apt_fields)  -> "light" | "medium" | "heavy"
problem(key)             -> None, or why the app cannot run here
                            (e.g. it needs OpenGL 3.3 and this Mac has 2.1)

key is a Debian package name or a Flathub app id. Known apps are listed in
/usr/share/mangos/store-requirements.conf; other Debian apps are judged
from their size and what they are built on (Electron, Java, web engines),
other Flathub apps count as medium (they bring their own runtime).
The machine's facts (OpenGL version from glxinfo, CPU features, memory)
are measured once per boot and cached in ~/.cache/mangos/machine.json."""
import json, os, re, subprocess

CONF = "/usr/share/mangos/store-requirements.conf"
CACHE = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "mangos", "machine.json")
_table = None
_machine = None


def table():
    """{key: (weight or None, [needs...])}"""
    global _table
    if _table is None:
        _table = {}
        try:
            for line in open(CONF):
                line = line.split("#", 1)[0].split()
                if len(line) >= 2:
                    w = line[1] if line[1] in ("light", "medium", "heavy") else None
                    _table[line[0]] = (w, line[2:])
        except OSError:
            pass
    return _table


def _boot_id():
    try:
        return open("/proc/sys/kernel/random/boot_id").read().strip()
    except OSError:
        return ""


def _gl():
    """(best OpenGL version as a tuple, renderer string); (None, '') if unknown."""
    try:
        out = subprocess.run(["glxinfo", "-B"], capture_output=True, text=True, timeout=8).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    vers = [tuple(int(x) for x in m) for m in
            re.findall(r"^OpenGL (?:core profile )?version string: (\d+)\.(\d+)", out, re.M)]
    ren = re.search(r"^OpenGL renderer string: (.*)$", out, re.M)
    return (max(vers) if vers else None), (ren.group(1).strip() if ren else "")


def machine():
    global _machine
    if _machine is not None:
        return _machine
    boot = _boot_id()
    try:
        m = json.load(open(CACHE))
        if m.get("boot") == boot and m.get("v") == 1:
            _machine = m
            return m
    except (OSError, ValueError):
        pass
    flags = set()
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("flags"):
                flags = set(line.split(":", 1)[1].split())
                break
    except OSError:
        pass
    ram = 0
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemTotal:"):
                ram = int(line.split()[1]) // 1024
    except OSError:
        pass
    gl, renderer = _gl()
    m = {"v": 1, "boot": boot, "flags": sorted(flags), "ram_mb": ram,
         "gl": list(gl) if gl else None, "renderer": renderer}
    if gl is not None:                 # only cache a complete measurement
        try:
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            json.dump(m, open(CACHE, "w"))
        except OSError:
            pass
    _machine = m
    return m


def has_vulkan(m):
    """No Vulkan driver exists for the GPUs of Macs before ~2012 with OpenGL
    below 4.x (Intel GMA X3100/4500, GeForce 9400M/320M, Radeon X1600/HD 2600);
    llvmpipe (software) does not count as a GPU."""
    gl = tuple(m.get("gl") or ())
    return bool(gl) and gl >= (4, 2) and "llvmpipe" not in m.get("renderer", "")


CPU_NAMES = {"sse4_2": "SSE4.2", "avx": "AVX", "avx2": "AVX2", "sse4_1": "SSE4.1", "ssse3": "SSSE3"}


def problem(key, tr):
    """Why this app cannot run on this Mac, or None. tr(en, it) translates."""
    entry = table().get(key)
    if not entry or not entry[1]:
        return None
    m = machine()
    flags = set(m.get("flags") or ())
    gl = tuple(m.get("gl") or ()) or None
    for need in entry[1]:
        if need.startswith("gl="):
            want = tuple(int(x) for x in need[3:].split("."))
            if gl is not None and gl < want:
                have = ".".join(map(str, gl))
                return tr(f"Needs OpenGL {need[3:]} graphics; this Mac has OpenGL {have}.",
                          f"Richiede una grafica OpenGL {need[3:]}; questo Mac ha OpenGL {have}.")
        elif need == "vulkan":
            if gl is not None and not has_vulkan(m):
                return tr("Needs Vulkan graphics, which this Mac's graphics card does not have.",
                          "Richiede la grafica Vulkan, che la scheda grafica di questo Mac non ha.")
        elif need.startswith("cpu="):
            for f in need[4:].split("+"):
                if flags and f not in flags:
                    n = CPU_NAMES.get(f, f.upper())
                    return tr(f"Needs a newer processor (with {n}) than this Mac's.",
                              f"Richiede un processore più recente (con {n}) di quello di questo Mac.")
        elif need.startswith("ram="):
            gb = float(need[4:])
            if m.get("ram_mb") and m["ram_mb"] < gb * 1024 * 0.93:
                return tr(f"Needs at least {need[4:]} GB of memory.",
                          f"Richiede almeno {need[4:]} GB di memoria.")
    return None


HEAVY_DEPS = ("electron", "default-jre", "openjdk-", "java-runtime", "libcef")
MEDIUM_DEPS = ("libqt6webengine", "libqt5webengine", "libwebkit2gtk", "libwebkitgtk", "mono-runtime",
               "libmono-", "libkf6", "libkf5", "python3-pyqt", "nodejs")


def weight(key, apt_fields=None, flatpak=False):
    entry = table().get(key)
    if entry and entry[0]:
        return entry[0]
    if flatpak:
        return "medium"
    f = apt_fields or {}
    deps = (f.get("Depends", "") + "," + f.get("Pre-Depends", "")).lower()
    size_mb = int(f.get("Installed-Size", "0") or 0) / 1024
    if any(d in deps for d in HEAVY_DEPS) or ("libnss3" in deps and "libgbm1" in deps and size_mb > 120):
        return "heavy"                 # Electron / Chromium-based or Java
    if size_mb > 250:
        return "heavy"
    if size_mb > 40 or any(d in deps for d in MEDIUM_DEPS):
        return "medium"
    return "light"


def describe(w, tr):
    """(label, explanation) for a weight."""
    m = machine()
    ram = round((m.get("ram_mb") or 0) / 1024)
    mac = tr(f" on this Mac ({ram} GB)", f" su questo Mac ({ram} GB)") if ram else ""
    return {
        "light": (tr("Light", "Leggera"),
                  tr("Starts fast and uses little memory" + mac + ".",
                     "Si apre in fretta e usa poca memoria" + mac + ".")),
        "medium": (tr("Medium", "Media"),
                   tr("Runs well; with many other apps open it may slow down" + mac + ".",
                      "Funziona bene; con molte altre app aperte può rallentare" + mac + ".")),
        "heavy": (tr("Heavy", "Pesante"),
                  tr("Uses a lot of memory and processor" + mac + ": close other apps while using it.",
                     "Usa molta memoria e processore" + mac + ": chiudi le altre app mentre la usi.")),
    }[w]
