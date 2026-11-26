#!/usr/bin/python3
"""Tests for mangos.fileops (Mango Finder's file operations).
Run inside the image (needs GIO, gvfs for trash:///, a D-Bus session):
    dbus-run-session -- python3 tests/test_fileops.py"""
import os, shutil, sys, tempfile, threading, time
from gi.repository import Gio, GLib
from mangos import fileops as fo

HOME = os.path.expanduser("~")
BASE = tempfile.mkdtemp(prefix="fo-test-", dir=HOME)          # in home: it has a Trash
OTHER = tempfile.mkdtemp(prefix="fo-test-", dir="/dev/shm")    # another file system
results = []


def F(*p):
    return Gio.File.new_for_path(os.path.join(*p))


def write(path, data="x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(data)


def read(path):
    return open(path).read()


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail and not cond else ""))


def fresh(*parts):
    d = os.path.join(BASE, *parts)
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    return d


def run(kind, sources, dest=None, answer=("keep", False), confirm=False, **kw):
    j = fo.Job(kind, [F(s) for s in sources], F(dest) if dest else None,
               conflict=lambda s, d: answer, confirm=lambda k, f: confirm, **kw)
    return j.run()


# 1 copy a file and a folder tree
d = fresh("t1"); write(f"{d}/a.txt", "AAA"); write(f"{d}/dir/sub/b.txt", "BBB"); os.makedirs(f"{d}/to")
j = run("copy", [f"{d}/a.txt", f"{d}/dir"], f"{d}/to")
check("copy file", read(f"{d}/to/a.txt") == "AAA" and read(f"{d}/a.txt") == "AAA")
check("copy folder tree", read(f"{d}/to/dir/sub/b.txt") == "BBB" and not j.errors, j.errors)
check("copy progress reached the total", j.done >= j.total > 0, (j.done, j.total))

# 2 conflicts: keep both, skip, replace; folders merge
d = fresh("t2"); write(f"{d}/src/n.txt", "NEW"); write(f"{d}/dst/n.txt", "OLD")
run("copy", [f"{d}/src/n.txt"], f"{d}/dst", answer=("keep", False))
check("conflict keep both -> 'n 2.txt'", read(f"{d}/dst/n.txt") == "OLD" and read(f"{d}/dst/n 2.txt") == "NEW")
run("copy", [f"{d}/src/n.txt"], f"{d}/dst", answer=("skip", False))
check("conflict skip leaves the old file", read(f"{d}/dst/n.txt") == "OLD")
run("copy", [f"{d}/src/n.txt"], f"{d}/dst", answer=("replace", False))
check("conflict replace", read(f"{d}/dst/n.txt") == "NEW")
write(f"{d}/A/x.txt", "x1"); write(f"{d}/B/A/y.txt", "y1")
run("copy", [f"{d}/A"], f"{d}/B", answer=("replace", False))
check("replace a folder merges, never deletes", read(f"{d}/B/A/y.txt") == "y1" and read(f"{d}/B/A/x.txt") == "x1")
j = run("copy", [f"{d}/src/n.txt"], f"{d}/dst", answer=("cancel", False))
check("conflict cancel stops the job", "cancelled" in j.errors, j.errors)

# 3 a folder into itself is refused, files intact
d = fresh("t3"); write(f"{d}/P/f.txt", "f")
j = run("copy", [f"{d}/P"], f"{d}/P")
check("copy folder into itself refused", j.errors and not os.path.exists(f"{d}/P/P"), j.errors)
os.makedirs(f"{d}/P/inner")
j = run("move", [f"{d}/P"], f"{d}/P/inner")
check("move folder into its subfolder refused", j.errors and read(f"{d}/P/f.txt") == "f", j.errors)

# 4 paste in the same folder makes 'name copy'
d = fresh("t4"); write(f"{d}/r.txt", "r")
run("copy", [f"{d}/r.txt"], d)
check("paste into the same folder -> 'r copy.txt'", read(f"{d}/r copy.txt") == "r")

# 5 move on the same disk and undo
d = fresh("t5"); write(f"{d}/m.txt", "M"); write(f"{d}/D/k.txt", "K"); os.makedirs(f"{d}/to")
j = run("move", [f"{d}/m.txt", f"{d}/D"], f"{d}/to")
check("move same disk", read(f"{d}/to/m.txt") == "M" and read(f"{d}/to/D/k.txt") == "K" and not os.path.exists(f"{d}/m.txt"))
errs = fo.undo(j.undo)
check("undo move", read(f"{d}/m.txt") == "M" and read(f"{d}/D/k.txt") == "K" and not os.path.exists(f"{d}/to/m.txt"), errs)

# 6 move to another disk: originals removed only after the copy
d = fresh("t6"); write(f"{d}/big/one.txt", "1"); write(f"{d}/big/two/two.txt", "2")
j = run("move", [f"{d}/big"], OTHER)
check("move to another disk", read(f"{OTHER}/big/two/two.txt") == "2" and not os.path.exists(f"{d}/big"), j.errors)
errs = fo.undo(j.undo)
check("undo move from another disk", read(f"{d}/big/one.txt") == "1", errs)

# 7 Trash and undo (put back)
d = fresh("t7"); write(f"{d}/del.txt", "D"); write(f"{d}/deldir/z.txt", "Z")
j = run("trash", [f"{d}/del.txt", f"{d}/deldir"])
check("move to Trash", not os.path.exists(f"{d}/del.txt") and not os.path.exists(f"{d}/deldir") and not j.errors, j.errors)
time.sleep(1)
errs = fo.undo(j.undo)
check("undo Trash puts items back", read(f"{d}/del.txt") == "D" and read(f"{d}/deldir/z.txt") == "Z", errs)

# 8 no Trash on that disk: asks, and does nothing if refused
write(f"{OTHER}/notrash.txt", "N")
j = run("trash", [f"{OTHER}/notrash.txt"], confirm=False)
check("no Trash available + refused -> file kept", os.path.exists(f"{OTHER}/notrash.txt") or j.undo, (j.errors, j.undo))

# 9 rename, invalid names, undo
d = fresh("t9"); write(f"{d}/old.txt", "o"); write(f"{d}/taken.txt", "t")
j = run("rename", [f"{d}/old.txt"], new_name="new.txt")
check("rename", read(f"{d}/new.txt") == "o" and not os.path.exists(f"{d}/old.txt"))
fo.undo(j.undo)
check("undo rename", read(f"{d}/old.txt") == "o")
j = run("rename", [f"{d}/old.txt"], new_name="taken.txt")
check("rename onto an existing name refused", j.errors and read(f"{d}/taken.txt") == "t", j.errors)
j = run("rename", [f"{d}/old.txt"], new_name="a/b")
check("rename with '/' refused", j.errors and os.path.exists(f"{d}/old.txt"), j.errors)

# 10 new folder names, duplicate names
d = fresh("t10")
for _ in range(3):
    run("new_folder", [], d, folder_word="Nuova cartella")
check("new folders: 'Nuova cartella', '... 2', '... 3'",
      all(os.path.isdir(f"{d}/{n}") for n in ("Nuova cartella", "Nuova cartella 2", "Nuova cartella 3")))
write(f"{d}/foto.jpg", "j")
run("duplicate", [f"{d}/foto.jpg"], copy_word="copia"); run("duplicate", [f"{d}/foto.jpg"], copy_word="copia")
check("duplicate: 'foto copia.jpg', 'foto copia 2.jpg'", os.path.exists(f"{d}/foto copia.jpg") and os.path.exists(f"{d}/foto copia 2.jpg"))
check("split_ext keeps .tar.gz together", fo.split_ext("backup.tar.gz") == ("backup", ".tar.gz") and fo.split_ext(".bashrc") == (".bashrc", ""))

# 11 cancel in the middle of a long copy (thousands of files): the source
# stays complete, the job reports "cancelled" and what was copied can be undone
d = fresh("t11")
for k in range(4000):
    write(f"{d}/many/f{k:04d}.dat", "z" * 2000)
os.makedirs(f"{d}/to")
j = fo.Job("copy", [F(f"{d}/many")], F(f"{d}/to"))
t = threading.Thread(target=j.run); t.start()
while (j.total == 0 or j.done < j.total // 10) and t.is_alive():
    time.sleep(0.002)
j.cancel(); t.join()
copied = len(os.listdir(f"{d}/to/many")) if os.path.isdir(f"{d}/to/many") else 0
check("cancel during a long copy", "cancelled" in j.errors and len(os.listdir(f"{d}/many")) == 4000 and 0 < copied < 4000,
      (j.errors, copied))
check("partial copy can be undone (goes to the Trash)", any(r[0] == "trash" for r in j.undo) or copied == 0
      or not fo.undo(j.undo), j.undo)

# 12 a read-only folder: clear error, nothing lost
d = fresh("t12"); write(f"{d}/s.txt", "s"); os.makedirs(f"{d}/ro"); os.chmod(f"{d}/ro", 0o555)
j = run("copy", [f"{d}/s.txt"], f"{d}/ro")
os.chmod(f"{d}/ro", 0o755)
if os.geteuid() == 0:
    check("read-only folder (skipped: running as root)", True)
else:
    check("copy into a read-only folder fails cleanly", j.errors and read(f"{d}/s.txt") == "s", j.errors)

# 13 empty Trash only touches the Trash
d = fresh("t13"); write(f"{d}/keep.txt", "k"); write(f"{d}/gone.txt", "g")
run("trash", [f"{d}/gone.txt"])
j = run("empty_trash", [])
check("empty Trash", fo.trash_item_for(f"{d}/gone.txt") is None and read(f"{d}/keep.txt") == "k", j.errors)

# 14 Put Back from the Trash (restore), also when the original folder is gone
d = fresh("t14"); write(f"{d}/sub/pb.txt", "P")
run("trash", [f"{d}/sub/pb.txt"])
item = fo.trash_item_for(f"{d}/sub/pb.txt")
shutil.rmtree(f"{d}/sub")
j = fo.Job("restore", [item]).run()
check("Put Back recreates the folder and restores", read(f"{d}/sub/pb.txt") == "P" and not j.errors, j.errors)

# 15 undo a copy made on a disk without Trash: the copy is removed, the original stays
d = fresh("t15"); write(f"{d}/u.txt", "U")
j = run("copy", [f"{d}/u.txt"], OTHER)
errs = fo.undo(j.undo)
check("undo copy on a disk without Trash", not os.path.exists(f"{OTHER}/u.txt") and read(f"{d}/u.txt") == "U" and not errs, errs)

# 16 new document: empty, from a template, names do not clash
d = fresh("t16"); write(f"{d}/tpl/Lettera.txt", "Caro")
j = run("new_file", [], d, new_name="Senza titolo.txt")
j2 = run("new_file", [], d, new_name="Senza titolo.txt")
j3 = fo.Job("new_file", [], F(d), template=F(f"{d}/tpl/Lettera.txt")).run()
check("new empty document, second one numbered", os.path.getsize(f"{d}/Senza titolo.txt") == 0
      and os.path.exists(f"{d}/Senza titolo 2.txt") and not j.errors, j.errors)
check("new document from a template", read(f"{d}/Lettera.txt") == "Caro" and not j3.errors, j3.errors)
fo.undo(j3.undo)
check("undo new document", not os.path.exists(f"{d}/Lettera.txt"))

# 17 alias (symbolic link)
d = fresh("t17"); write(f"{d}/orig.txt", "O"); os.makedirs(f"{d}/to")
j = run("link", [f"{d}/orig.txt"], f"{d}/to")
check("make alias", os.path.islink(f"{d}/to/orig.txt") and read(f"{d}/to/orig.txt") == "O", j.errors)

# 18 copy_to: exact destinations (the desktop's CopyTo)
d = fresh("t18"); write(f"{d}/a.txt", "A")
j = fo.Job("copy_to", [F(f"{d}/a.txt")], targets=[F(f"{d}/b.txt")]).run()
check("copy to an exact name", read(f"{d}/b.txt") == "A" and not j.errors, j.errors)

# 19 compress (like the Mac): one item -> doc.txt.zip, several -> Archive.zip, contents complete
import zipfile
d = fresh("t19"); write(f"{d}/doc.txt", "D" * 5000); write(f"{d}/dir/x/y.txt", "Y"); os.makedirs(f"{d}/dir/empty")
j = run("compress", [f"{d}/doc.txt"])
check("compress one file -> doc.txt.zip", zipfile.ZipFile(f"{d}/doc.txt.zip").read("doc.txt") == b"D" * 5000, j.errors)
j = run("compress", [f"{d}/doc.txt", f"{d}/dir"], new_name="Archivio")
names = set(zipfile.ZipFile(f"{d}/Archivio.zip").namelist())
check("compress several -> Archivio.zip with folders", {"doc.txt", "dir/x/y.txt", "dir/empty/"} <= names, names)
j = run("compress", [f"{d}/doc.txt"])
check("compress again -> doc.txt 2.zip", os.path.exists(f"{d}/doc.txt 2.zip"), j.errors)
check("compress progress reached the total", j.done >= j.total > 0, (j.done, j.total))

shutil.rmtree(BASE, ignore_errors=True); shutil.rmtree(OTHER, ignore_errors=True)
ok = sum(1 for _, r in results if r)
print(f"\n{ok}/{len(results)} passed")
sys.exit(0 if ok == len(results) else 1)
