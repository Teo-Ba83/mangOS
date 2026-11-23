"""Intel Macs 2006-2012: names, hardware and how well MangOS runs on them.

lookup("MacBook4,1") -> Model or None. The model id is the DMI product name
(/sys/class/dmi/id/product_name). Status:
  tested       tried on the real machine
  same         same graphics, Wi-Fi and firmware as a tested model
  untested     should work (drivers are in MangOS), nobody has tried yet
  unsupported  32-bit processor (Core Duo / Core Solo): MangOS is 64-bit
Wi-Fi and graphics are the chip families the model shipped with (some
models had more than one option). docs/MAC-MODELS.md is generated from this
table (python3 -m mangos.macmodels --markdown)."""
import collections, sys

Model = collections.namedtuple("Model", "id family year_en year_it cpu64 efi graphics wifi status note")

# graphics families: intel, nvidia (nouveau), amd (radeon); wifi: broadcom (wl), atheros (ath9k)
_T = [
    # id            family          year (en)              year (it)                64    efi  graphics                         wifi                 status        note
    ("MacBook1,1",  "MacBook",      "13-inch, 2006",       "13 pollici, 2006",      False, 32, "Intel GMA 950",                 "Atheros",           "unsupported", ""),
    ("MacBook2,1",  "MacBook",      "13-inch, late 2006 / mid 2007", "13 pollici, fine 2006 / metà 2007", True, 32, "Intel GMA 950", "Atheros", "untested", "efi32"),
    ("MacBook3,1",  "MacBook",      "13-inch, late 2007",  "13 pollici, fine 2007", True, 64, "Intel GMA X3100",               "Broadcom or Atheros", "same",      ""),
    ("MacBook4,1",  "MacBook",      "13-inch, early 2008", "13 pollici, inizio 2008", True, 64, "Intel GMA X3100",             "Broadcom or Atheros", "tested",    ""),
    ("MacBook5,1",  "MacBook",      "13-inch aluminium, late 2008", "13 pollici alluminio, fine 2008", True, 64, "NVIDIA GeForce 9400M", "Broadcom", "untested", ""),
    ("MacBook5,2",  "MacBook",      "13-inch, early / mid 2009", "13 pollici, inizio / metà 2009", True, 64, "NVIDIA GeForce 9400M", "Broadcom", "untested", ""),
    ("MacBook6,1",  "MacBook",      "13-inch, late 2009",  "13 pollici, fine 2009", True, 64, "NVIDIA GeForce 9400M",          "Broadcom",          "untested", ""),
    ("MacBook7,1",  "MacBook",      "13-inch, mid 2010",   "13 pollici, metà 2010", True, 64, "NVIDIA GeForce 320M",           "Broadcom",          "untested", ""),

    ("MacBookAir1,1", "MacBook Air", "2008",               "2008",                  True, 64, "Intel GMA X3100",               "Broadcom",          "untested", ""),
    ("MacBookAir2,1", "MacBook Air", "late 2008 / mid 2009", "fine 2008 / metà 2009", True, 64, "NVIDIA GeForce 9400M",       "Broadcom",          "untested", ""),
    ("MacBookAir3,1", "MacBook Air", "11-inch, late 2010", "11 pollici, fine 2010", True, 64, "NVIDIA GeForce 320M",           "Broadcom",          "untested", ""),
    ("MacBookAir3,2", "MacBook Air", "13-inch, late 2010", "13 pollici, fine 2010", True, 64, "NVIDIA GeForce 320M",           "Broadcom",          "untested", ""),
    ("MacBookAir4,1", "MacBook Air", "11-inch, mid 2011",  "11 pollici, metà 2011", True, 64, "Intel HD Graphics 3000",        "Broadcom",          "untested", ""),
    ("MacBookAir4,2", "MacBook Air", "13-inch, mid 2011",  "13 pollici, metà 2011", True, 64, "Intel HD Graphics 3000",        "Broadcom",          "untested", ""),
    ("MacBookAir5,1", "MacBook Air", "11-inch, mid 2012",  "11 pollici, metà 2012", True, 64, "Intel HD Graphics 4000",        "Broadcom",          "untested", ""),
    ("MacBookAir5,2", "MacBook Air", "13-inch, mid 2012",  "13 pollici, metà 2012", True, 64, "Intel HD Graphics 4000",        "Broadcom",          "untested", ""),

    ("MacBookPro1,1", "MacBook Pro", "15-inch, early 2006", "15 pollici, inizio 2006", False, 32, "ATI Radeon X1600",          "Atheros",           "unsupported", ""),
    ("MacBookPro1,2", "MacBook Pro", "17-inch, 2006",     "17 pollici, 2006",      False, 32, "ATI Radeon X1600",              "Atheros",           "unsupported", ""),
    ("MacBookPro2,1", "MacBook Pro", "17-inch, late 2006", "17 pollici, fine 2006", True, 32, "ATI Radeon X1600",              "Atheros",           "untested", "efi32"),
    ("MacBookPro2,2", "MacBook Pro", "15-inch, late 2006", "15 pollici, fine 2006", True, 32, "ATI Radeon X1600",              "Atheros",           "untested", "efi32"),
    ("MacBookPro3,1", "MacBook Pro", "mid / late 2007",   "metà / fine 2007",      True, 64, "NVIDIA GeForce 8600M GT",        "Atheros or Broadcom", "untested", ""),
    ("MacBookPro4,1", "MacBook Pro", "early 2008",        "inizio 2008",           True, 64, "NVIDIA GeForce 8600M GT",        "Atheros or Broadcom", "untested", ""),
    ("MacBookPro5,1", "MacBook Pro", "15-inch, late 2008", "15 pollici, fine 2008", True, 64, "NVIDIA GeForce 9400M + 9600M GT", "Broadcom",       "untested", "dualgpu"),
    ("MacBookPro5,2", "MacBook Pro", "17-inch, 2009",     "17 pollici, 2009",      True, 64, "NVIDIA GeForce 9400M + 9600M GT", "Broadcom",          "untested", "dualgpu"),
    ("MacBookPro5,3", "MacBook Pro", "15-inch, mid 2009", "15 pollici, metà 2009", True, 64, "NVIDIA GeForce 9400M + 9600M GT", "Broadcom",          "untested", "dualgpu"),
    ("MacBookPro5,4", "MacBook Pro", "15-inch, mid 2009", "15 pollici, metà 2009", True, 64, "NVIDIA GeForce 9400M",          "Broadcom",          "untested", ""),
    ("MacBookPro5,5", "MacBook Pro", "13-inch, mid 2009", "13 pollici, metà 2009", True, 64, "NVIDIA GeForce 9400M",          "Broadcom",          "untested", ""),
    ("MacBookPro6,1", "MacBook Pro", "17-inch, mid 2010", "17 pollici, metà 2010", True, 64, "Intel HD + NVIDIA GeForce GT 330M", "Broadcom",        "untested", "gmux"),
    ("MacBookPro6,2", "MacBook Pro", "15-inch, mid 2010", "15 pollici, metà 2010", True, 64, "Intel HD + NVIDIA GeForce GT 330M", "Broadcom",        "untested", "gmux"),
    ("MacBookPro7,1", "MacBook Pro", "13-inch, mid 2010", "13 pollici, metà 2010", True, 64, "NVIDIA GeForce 320M",           "Broadcom",          "untested", ""),
    ("MacBookPro8,1", "MacBook Pro", "13-inch, 2011",     "13 pollici, 2011",      True, 64, "Intel HD Graphics 3000",        "Broadcom",          "untested", ""),
    ("MacBookPro8,2", "MacBook Pro", "15-inch, 2011",     "15 pollici, 2011",      True, 64, "Intel HD 3000 + AMD Radeon HD 6490M / 6750M / 6770M", "Broadcom", "untested", "amd2011"),
    ("MacBookPro8,3", "MacBook Pro", "17-inch, 2011",     "17 pollici, 2011",      True, 64, "Intel HD 3000 + AMD Radeon HD 6750M / 6770M", "Broadcom", "untested", "amd2011"),
    ("MacBookPro9,1", "MacBook Pro", "15-inch, mid 2012", "15 pollici, metà 2012", True, 64, "Intel HD 4000 + NVIDIA GeForce GT 650M", "Broadcom",   "untested", "gmux"),
    ("MacBookPro9,2", "MacBook Pro", "13-inch, mid 2012", "13 pollici, metà 2012", True, 64, "Intel HD Graphics 4000",        "Broadcom",          "untested", ""),
    ("MacBookPro10,1", "MacBook Pro", "Retina, 15-inch, mid 2012", "Retina, 15 pollici, metà 2012", True, 64, "Intel HD 4000 + NVIDIA GeForce GT 650M", "Broadcom", "untested", "gmux"),
    ("MacBookPro10,2", "MacBook Pro", "Retina, 13-inch, late 2012", "Retina, 13 pollici, fine 2012", True, 64, "Intel HD Graphics 4000", "Broadcom", "untested", ""),

    ("iMac4,1",     "iMac",         "early 2006",          "inizio 2006",           False, 32, "ATI Radeon X1600",             "Atheros",           "unsupported", ""),
    ("iMac4,2",     "iMac",         "17-inch, mid 2006",   "17 pollici, metà 2006", False, 32, "Intel GMA 950",                "Atheros",           "unsupported", ""),
    ("iMac5,1",     "iMac",         "late 2006",           "fine 2006",             True, 32, "ATI Radeon X1600 or NVIDIA GeForce 7300 GT / 7600 GT", "Atheros", "untested", "efi32"),
    ("iMac5,2",     "iMac",         "17-inch, late 2006",  "17 pollici, fine 2006", True, 32, "Intel GMA 950",                 "Atheros",           "untested", "efi32"),
    ("iMac6,1",     "iMac",         "24-inch, late 2006",  "24 pollici, fine 2006", True, 32, "NVIDIA GeForce 7300 GT / 7600 GT", "Atheros",        "untested", "efi32"),
    ("iMac7,1",     "iMac",         "mid 2007",            "metà 2007",             True, 64, "ATI Radeon HD 2400 XT / 2600 Pro", "Atheros",        "untested", ""),
    ("iMac8,1",     "iMac",         "early 2008",          "inizio 2008",           True, 64, "ATI Radeon HD 2400 / 2600 or NVIDIA GeForce 8800 GS", "Atheros or Broadcom", "untested", ""),
    ("iMac9,1",     "iMac",         "early / mid 2009",    "inizio / metà 2009",    True, 64, "NVIDIA GeForce 9400M / GT 120 / GT 130", "Atheros or Broadcom", "untested", ""),
    ("iMac10,1",    "iMac",         "late 2009",           "fine 2009",             True, 64, "NVIDIA GeForce 9400M or ATI Radeon HD 4670", "Atheros", "untested", ""),
    ("iMac11,1",    "iMac",         "27-inch, late 2009",  "27 pollici, fine 2009", True, 64, "ATI Radeon HD 4850",            "Atheros",           "untested", ""),
    ("iMac11,2",    "iMac",         "21.5-inch, mid 2010", "21,5 pollici, metà 2010", True, 64, "ATI Radeon HD 4670",          "Atheros",           "untested", ""),
    ("iMac11,3",    "iMac",         "27-inch, mid 2010",   "27 pollici, metà 2010", True, 64, "ATI Radeon HD 5670 / 5750",     "Atheros",           "untested", ""),
    ("iMac12,1",    "iMac",         "21.5-inch, mid 2011", "21,5 pollici, metà 2011", True, 64, "AMD Radeon HD 6750M / 6770M", "Atheros",           "untested", ""),
    ("iMac12,2",    "iMac",         "27-inch, mid 2011",   "27 pollici, metà 2011", True, 64, "AMD Radeon HD 6770M / 6970M",   "Atheros",           "untested", ""),
    ("iMac13,1",    "iMac",         "21.5-inch, late 2012", "21,5 pollici, fine 2012", True, 64, "NVIDIA GeForce GT 640M / 650M", "Broadcom",        "untested", ""),
    ("iMac13,2",    "iMac",         "27-inch, late 2012",  "27 pollici, fine 2012", True, 64, "NVIDIA GeForce GTX 660M / 675MX / 680MX", "Broadcom", "untested", ""),

    ("Macmini1,1",  "Mac mini",     "early 2006",          "inizio 2006",           False, 32, "Intel GMA 950",                "Atheros",           "unsupported", ""),
    ("Macmini2,1",  "Mac mini",     "mid 2007",            "metà 2007",             True, 32, "Intel GMA 950",                 "Atheros",           "untested", "efi32"),
    ("Macmini3,1",  "Mac mini",     "early / late 2009",   "inizio / fine 2009",    True, 64, "NVIDIA GeForce 9400M",          "Atheros or Broadcom", "untested", ""),
    ("Macmini4,1",  "Mac mini",     "mid 2010",            "metà 2010",             True, 64, "NVIDIA GeForce 320M",           "Broadcom",          "untested", ""),
    ("Macmini5,1",  "Mac mini",     "mid 2011",            "metà 2011",             True, 64, "Intel HD Graphics 3000",        "Broadcom",          "untested", ""),
    ("Macmini5,2",  "Mac mini",     "mid 2011",            "metà 2011",             True, 64, "AMD Radeon HD 6630M",           "Broadcom",          "untested", ""),
    ("Macmini5,3",  "Mac mini",     "server, mid 2011",    "server, metà 2011",     True, 64, "Intel HD Graphics 3000",        "Broadcom",          "untested", ""),
    ("Macmini6,1",  "Mac mini",     "late 2012",           "fine 2012",             True, 64, "Intel HD Graphics 4000",        "Broadcom",          "untested", ""),
    ("Macmini6,2",  "Mac mini",     "late 2012",           "fine 2012",             True, 64, "Intel HD Graphics 4000",        "Broadcom",          "untested", ""),

    ("MacPro1,1",   "Mac Pro",      "2006",                "2006",                  True, 32, "NVIDIA GeForce 7300 GT or ATI Radeon X1900 XT", "Atheros or Broadcom (option)", "untested", "efi32"),
    ("MacPro2,1",   "Mac Pro",      "2007",                "2007",                  True, 32, "NVIDIA / ATI (various)",        "Atheros or Broadcom (option)", "untested", "efi32"),
    ("MacPro3,1",   "Mac Pro",      "early 2008",          "inizio 2008",           True, 64, "ATI Radeon HD 2600 XT or NVIDIA GeForce 8800 GT", "Broadcom or Atheros (option)", "untested", ""),
    ("MacPro4,1",   "Mac Pro",      "2009",                "2009",                  True, 64, "NVIDIA GeForce GT 120 or ATI Radeon HD 4870", "Atheros or Broadcom (option)", "untested", ""),
    ("MacPro5,1",   "Mac Pro",      "2010 / 2012",         "2010 / 2012",           True, 64, "ATI Radeon HD 5770 / 5870",     "Atheros or Broadcom (option)", "untested", ""),
]
MODELS = {r[0]: Model(*r) for r in _T}

NOTES = {
    "efi32": ("32-bit EFI firmware: use the MangOS EFI32 image (MangOS-<version>-efi32.iso).",
              "Firmware EFI a 32 bit: usa l'immagine MangOS EFI32 (MangOS-<versione>-efi32.iso)."),
    "dualgpu": ("Two NVIDIA graphics chips: MangOS uses the one chosen in macOS's Energy Saver (9400M by default).",
                "Due chip grafici NVIDIA: MangOS usa quello scelto in macOS in Risparmio Energia (di base la 9400M)."),
    "gmux": ("Switchable graphics (Intel + NVIDIA): the screen is driven by the chip active at startup.",
             "Grafica commutabile (Intel + NVIDIA): lo schermo usa il chip attivo all'avvio."),
    "amd2011": ("The AMD graphics chip of these models often fails with age (a hardware fault). If the screen "
                "freezes or stays black, start with 'MangOS (safe graphics)'.",
                "Il chip grafico AMD di questi modelli si guasta spesso con gli anni (difetto hardware). Se lo "
                "schermo si blocca o resta nero, avvia con 'MangOS (safe graphics)'."),
}

STATUS = {
    "tested": ("Tested", "Provato", "✅"),
    "same": ("Same hardware as a tested model", "Stesso hardware di un modello provato", "✅"),
    "untested": ("Should work, not tried yet", "Dovrebbe funzionare, non ancora provato", "❔"),
    "unsupported": ("Not supported: 32-bit processor", "Non supportato: processore a 32 bit", "❌"),
}


def lookup(product):
    return MODELS.get((product or "").strip())


def this_mac():
    try:
        return lookup(open("/sys/class/dmi/id/product_name").read())
    except OSError:
        return None


def name(m, tr):
    return f"{m.family} ({tr(m.year_en, m.year_it)})"


def image(m):
    """Which MangOS image starts this Mac: 'efi32', 'amd64' or None."""
    if not m.cpu64:
        return None
    return "efi32" if m.efi == 32 else "amd64"


def markdown():
    out = ["| Model | Identifier | Image | 64-bit CPU | EFI | Graphics | Wi-Fi | Status | Notes |",
           "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS.values():
        st = STATUS[m.status]
        img = {"efi32": "**EFI32**", "amd64": "amd64", None: "—"}[image(m)]
        out.append(f"| {m.family} ({m.year_en}) | `{m.id}` | {img} | {'yes' if m.cpu64 else '**no**'} | {m.efi}-bit | "
                   f"{m.graphics} | {m.wifi} | {st[2]} {st[0]} | {NOTES.get(m.note, ('',))[0]} |")
    return "\n".join(out)


if __name__ == "__main__":
    if "--markdown" in sys.argv:
        print(markdown())
    else:
        m = this_mac()
        print(f"{m.id}: {m.family} ({m.year_en}) - {STATUS[m.status][0]}" if m else "not a known Intel Mac (2006-2012)")
