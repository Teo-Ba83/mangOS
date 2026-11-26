"""File operations for Mango Finder: copy, move, Trash, rename, new folder,
new document, alias, compress (.zip), duplicate, empty Trash, with progress, cancel, conflicts and undo.

Everything goes through GIO (the layer Thunar and GNOME Files use), so local
disks, USB sticks, network shares and the Trash behave the same. Safety rules:
  - "delete" is always Move to Trash; files are destroyed only by Empty
    Trash, or when a place has no Trash and the user confirms it
  - an existing item is never replaced without asking (conflict callback);
    a folder is never replaced as a whole: "replace" merges into it
  - a folder cannot be copied or moved into itself
  - a move between two disks deletes the originals only after every file
    has been copied
  - jobs run in a worker thread and can be cancelled between (and inside)
    files; what was done until then is kept and can be undone
No GTK here: the caller passes callbacks (progress, conflict, confirm) and
runs them on its own thread; this module is tested on its own."""
import os, threading, time
from gi.repository import Gio, GLib

COPY_FLAGS = Gio.FileCopyFlags.NOFOLLOW_SYMLINKS | Gio.FileCopyFlags.ALL_METADATA
QUERY = "standard::name,standard::display-name,standard::type,standard::size,standard::is-symlink"
NOFOLLOW = Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS


class Cancelled(Exception):
    pass


class OpError(Exception):
    pass


def ftype(f):
    return f.query_file_type(NOFOLLOW, None)


def exists(f):
    return ftype(f) != Gio.FileType.UNKNOWN


def is_dir(f):
    return ftype(f) == Gio.FileType.DIRECTORY


def same_fs(a, b):
    """True if a and b (an existing file and a folder) are on the same file system."""
    try:
        ia = a.query_info("id::filesystem", NOFOLLOW, None).get_attribute_string("id::filesystem")
        ib = b.query_info("id::filesystem", NOFOLLOW, None).get_attribute_string("id::filesystem")
        return bool(ia) and ia == ib
    except GLib.Error:
        return False


def inside(child, parent):
    """True if child is parent or somewhere inside it."""
    return child.equal(parent) or child.has_prefix(parent)


def split_ext(name):
    """'photo.jpg' -> ('photo', '.jpg'); '.bashrc' -> ('.bashrc', ''); 'a.tar.gz' -> ('a', '.tar.gz')."""
    if name.startswith(".") and name.count(".") == 1:
        return name, ""
    for double in (".tar.gz", ".tar.xz", ".tar.bz2", ".tar.zst"):
        if name.lower().endswith(double) and len(name) > len(double):
            return name[:-len(double)], name[-len(double):]
    base, ext = os.path.splitext(name)
    return (base, ext) if base else (name, "")


def unique_name(folder, name, style="number", copy_word="copy"):
    """A name not used in folder: 'name 2.ext', 'name 3.ext'... or, for
    duplicates, 'name copy.ext', 'name copy 2.ext' (like the Mac)."""
    if not exists(folder.get_child(name)):
        return name
    base, ext = split_ext(name)
    if style == "copy":
        cand = f"{base} {copy_word}{ext}"
        if not exists(folder.get_child(cand)):
            return cand
        n = 2
        while exists(folder.get_child(f"{base} {copy_word} {n}{ext}")):
            n += 1
        return f"{base} {copy_word} {n}{ext}"
    n = 2
    while exists(folder.get_child(f"{base} {n}{ext}")):
        n += 1
    return f"{base} {n}{ext}"


class Job:
    """One operation. Run run() in a worker thread.
    progress(done_bytes, total_bytes, current_name)       - may be called often
    conflict(src, dst) -> ('replace'|'keep'|'skip'|'cancel', apply_to_all)
    confirm(kind, files) -> bool                            - e.g. 'no-trash'
    After run(): self.undo is a list describing how to undo what was done,
    self.created the top-level items made (to select them), self.errors."""
    def __init__(self, kind, sources, dest=None, progress=None, conflict=None, confirm=None, new_name=None,
                 copy_word="copy", folder_word="untitled folder", template=None, targets=None):
        self.kind, self.sources, self.dest = kind, list(sources), dest
        self.progress = progress or (lambda *a: None)
        self.conflict_cb = conflict or (lambda s, d: ("keep", False))
        self.confirm = confirm or (lambda kind, files: False)
        self.new_name, self.copy_word, self.folder_word = new_name, copy_word, folder_word
        self.template = template          # new_file: a Gio.File to start from (Templates folder)
        self.targets = targets            # copy_to: the exact destination of each source
        self.cancellable = Gio.Cancellable()
        self.undo, self.created, self.errors = [], [], []
        self.total = self.done = 0
        self.all_answer = None
        self.lock = threading.Lock()

    def cancel(self):
        self.cancellable.cancel()

    def check(self):
        if self.cancellable.is_cancelled():
            raise Cancelled()

    # ---- conflicts
    def resolve(self, src, dst):
        if self.all_answer:
            return self.all_answer
        answer, all_ = self.conflict_cb(src, dst)
        if answer == "cancel":
            self.cancel(); raise Cancelled()
        if all_:
            self.all_answer = answer
        return answer

    # ---- sizes, for the progress bar
    def size_of(self, f):
        self.check()
        try:
            info = f.query_info(QUERY, NOFOLLOW, self.cancellable)
        except GLib.Error:
            return 0
        if info.get_file_type() == Gio.FileType.DIRECTORY:
            total = 0
            try:
                en = f.enumerate_children(QUERY, NOFOLLOW, self.cancellable)
                for ci in en:
                    total += self.size_of(f.get_child(ci.get_name()))
                en.close(None)
            except GLib.Error:
                pass
            return total + 1
        return max(1, info.get_size())

    def bump(self, n, name):
        self.done += n
        self.progress(min(self.done, self.total), self.total, name)

    # ---- recursive copy
    def copy_one(self, src, dst):
        """Copies src to dst (dst does not exist, or the user said replace)."""
        self.check()
        if is_dir(src):
            if not exists(dst):
                dst.make_directory(self.cancellable)
            elif not is_dir(dst):
                raise OpError(f"{dst.get_basename()} exists and is not a folder")
            self.bump(1, src.get_basename())
            en = src.enumerate_children(QUERY, NOFOLLOW, self.cancellable)
            children = [ci.get_name() for ci in en]
            en.close(None)
            for name in children:
                self.check()
                s, d = src.get_child(name), dst.get_child(name)
                if exists(d):
                    if is_dir(s) and is_dir(d):
                        self.copy_one(s, d)            # merge folders
                        continue
                    a = self.resolve(s, d)
                    if a == "skip":
                        self.bump(self.size_of(s), name); continue
                    if a == "keep":
                        d = dst.get_child(unique_name(dst, name))
                    elif a == "replace" and is_dir(d) != is_dir(s):
                        raise OpError(f"cannot replace {name}: one is a folder, the other a file")
                self.copy_one(s, d)
            return
        start = self.done
        size = max(1, self.size_of(src))

        def cb(cur, tot, *_):
            self.done = start + cur
            self.progress(min(self.done, self.total), self.total, src.get_basename())
        flags = COPY_FLAGS | (Gio.FileCopyFlags.OVERWRITE if exists(dst) else Gio.FileCopyFlags.NONE)
        src.copy(dst, flags, self.cancellable, cb)
        self.done = start + size
        self.progress(min(self.done, self.total), self.total, src.get_basename())

    def delete_tree(self, f):
        """Permanent delete (only for a move between disks after a full copy, or Empty Trash)."""
        self.check()
        if is_dir(f):
            en = f.enumerate_children(QUERY, NOFOLLOW, self.cancellable)
            names = [ci.get_name() for ci in en]
            en.close(None)
            for n in names:
                self.delete_tree(f.get_child(n))
        f.delete(self.cancellable)

    # ---- the operations
    def run(self):
        try:
            getattr(self, "do_" + self.kind)()
        except Cancelled:
            self.errors.append("cancelled")
        except GLib.Error as e:
            if e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                self.errors.append("cancelled")
            else:
                self.errors.append(e.message)
        except OpError as e:
            self.errors.append(str(e))
        return self

    def target_for(self, src):
        """Where src goes in self.dest, after asking about a conflict; None = skip."""
        name = src.get_basename()
        dst = self.dest.get_child(name)
        if not exists(dst):
            return dst, False
        if dst.equal(src):                    # pasted where it already is: a copy next to it
            return self.dest.get_child(unique_name(self.dest, name, "copy", self.copy_word)), False
        a = self.resolve(src, dst)
        if a == "skip":
            return None, False
        if a == "keep":
            return self.dest.get_child(unique_name(self.dest, name)), False
        if is_dir(src) != is_dir(dst):
            raise OpError(f"cannot replace “{name}”: one is a folder, the other a file")
        return dst, True                      # replace (folders: merge)

    def guard(self):
        for s in self.sources:
            if is_dir(s) and inside(self.dest, s):
                raise OpError(f"“{s.get_basename()}” cannot go inside itself")

    def do_copy(self):
        self.guard()
        self.total = sum(self.size_of(s) for s in self.sources)
        self.progress(0, self.total, "")
        for s in self.sources:
            self.check()
            dst, replacing = self.target_for(s)
            if dst is None:
                self.bump(self.size_of(s), s.get_basename()); continue
            if not replacing:
                self.undo.append(("trash", dst))     # recorded first: a cancelled copy can be undone too
            self.created.append(dst)
            self.copy_one(s, dst)

    def do_move(self):
        self.guard()
        self.total = sum(self.size_of(s) for s in self.sources)
        self.progress(0, self.total, "")
        for s in self.sources:
            self.check()
            if s.get_parent() and s.get_parent().equal(self.dest):
                self.bump(self.size_of(s), s.get_basename()); continue      # already there
            dst, replacing = self.target_for(s)
            if dst is None:
                self.bump(self.size_of(s), s.get_basename()); continue
            size = self.size_of(s)
            if not replacing and same_fs(s, self.dest):
                try:
                    s.move(dst, Gio.FileCopyFlags.NOFOLLOW_SYMLINKS | Gio.FileCopyFlags.NO_FALLBACK_FOR_MOVE,
                           self.cancellable, None)
                    self.bump(size, s.get_basename())
                    self.created.append(dst); self.undo.append(("move", dst, s))
                    continue
                except GLib.Error as e:
                    if not (e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.NOT_SUPPORTED) or
                            e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.WOULD_RECURSE)):
                        raise
            # another disk (or a merge): copy everything, then remove the originals
            self.copy_one(s, dst)
            self.delete_tree(s)
            self.created.append(dst)
            if not replacing:
                self.undo.append(("move", dst, s))

    def do_trash(self):
        self.total = len(self.sources)
        cannot = []
        for i, s in enumerate(self.sources):
            self.check()
            orig = s.get_path()
            try:
                s.trash(self.cancellable)
                self.undo.append(("untrash", orig))
            except GLib.Error as e:
                if e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.NOT_SUPPORTED):
                    cannot.append(s)
                else:
                    raise
            self.progress(i + 1, self.total, s.get_basename())
        if cannot and self.confirm("no-trash", cannot):
            for s in cannot:
                self.delete_tree(s)

    def do_delete(self):
        """Permanent: Empty Trash, or delete from Trash. Never offered for normal files."""
        self.total = len(self.sources)
        for i, s in enumerate(self.sources):
            self.check()
            self.delete_tree(s)
            self.progress(i + 1, self.total, s.get_basename())

    def do_empty_trash(self):
        trash = Gio.File.new_for_uri("trash:///")
        en = trash.enumerate_children(QUERY, NOFOLLOW, self.cancellable)
        items = [trash.get_child(ci.get_name()) for ci in en]
        en.close(None)
        self.sources = items
        self.do_delete()

    def do_rename(self):
        f = self.sources[0]
        name = (self.new_name or "").strip()
        if not name or "/" in name or name in (".", ".."):
            raise OpError("invalid name")
        old = f.get_basename()
        if name == old:
            return
        target = f.get_parent().get_child(name)
        if exists(target) and name.lower() != old.lower():
            raise OpError(f"“{name}” already exists")
        new = f.set_display_name(name, self.cancellable)
        self.created.append(new)
        self.undo.append(("rename", new, old))

    def do_new_folder(self):
        name = unique_name(self.dest, self.new_name or self.folder_word)
        f = self.dest.get_child(name)
        f.make_directory(self.cancellable)
        self.created.append(f)
        self.undo.append(("trash", f))

    def do_new_file(self):
        """An empty document, or a copy of a template (File > New Document)."""
        name = unique_name(self.dest, self.new_name or (self.template.get_basename() if self.template else "untitled"))
        f = self.dest.get_child(name)
        if self.template is not None:
            self.template.copy(f, Gio.FileCopyFlags.NONE, self.cancellable, None)
        else:
            f.create(Gio.FileCreateFlags.NONE, self.cancellable).close(None)
        self.created.append(f)
        self.undo.append(("trash", f))

    def do_link(self):
        """Aliases (symbolic links) to the sources, in dest."""
        for s in self.sources:
            self.check()
            name = unique_name(self.dest, s.get_basename())
            f = self.dest.get_child(name)
            f.make_symbolic_link(s.get_path() or s.get_uri(), self.cancellable)
            self.created.append(f)
            self.undo.append(("trash", f))

    def do_copy_to(self):
        """Each source copied to its own exact destination (the desktop asks this)."""
        self.total = sum(self.size_of(s) for s in self.sources)
        for s, d in zip(self.sources, self.targets or []):
            self.check()
            if exists(d):
                a = self.resolve(s, d)
                if a == "skip":
                    continue
                if a == "keep":
                    d = d.get_parent().get_child(unique_name(d.get_parent(), d.get_basename()))
            else:
                self.undo.append(("trash", d))
            self.created.append(d)
            self.copy_one(s, d)

    def do_compress(self):
        """A .zip of the sources next to them, like the Mac's Compress:
        'name.ext.zip' for one item, 'Archive.zip' for several (new_name)."""
        import zipfile
        if not self.sources:
            return
        parent = self.dest or self.sources[0].get_parent()
        if any(s.get_path() is None for s in self.sources) or parent.get_path() is None:
            raise OpError("only files on this computer or on a drive can be compressed")
        base = self.sources[0].get_basename() if len(self.sources) == 1 else (self.new_name or "Archive")
        out = parent.get_child(unique_name(parent, base + ".zip"))
        self.total = sum(self.size_of(s) for s in self.sources)
        self.undo.append(("trash", out))
        self.created.append(out)
        try:
            with zipfile.ZipFile(out.get_path(), "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
                for s in self.sources:
                    root = s.get_path()
                    top = os.path.dirname(root)
                    if os.path.isdir(root) and not os.path.islink(root):
                        for d, dirs, files in os.walk(root):
                            self.check()
                            dirs.sort(); files.sort()
                            rel = os.path.relpath(d, top)
                            if not files and not dirs:       # keep empty folders
                                z.write(d, rel + "/")
                            self.bump(1, os.path.basename(d))
                            for n in files:
                                self.check()
                                p = os.path.join(d, n)
                                if os.path.islink(p) or not os.path.isfile(p):
                                    continue
                                self.zip_file(z, p, os.path.join(rel, n))
                    else:
                        self.zip_file(z, root, os.path.basename(root))
        except Cancelled:
            try:
                os.unlink(out.get_path())
            except OSError:
                pass
            self.undo.remove(("trash", out)); self.created.remove(out)
            raise
        except OSError as e:
            raise OpError(str(e))

    def zip_file(self, z, path, arc):
        import zipfile
        zi = zipfile.ZipInfo.from_file(path, arc)
        zi.compress_type = zipfile.ZIP_DEFLATED
        with open(path, "rb") as src, z.open(zi, "w", force_zip64=True) as dst:
            while True:
                self.check()
                buf = src.read(1 << 20)
                if not buf:
                    break
                dst.write(buf)
                self.bump(len(buf), os.path.basename(path))

    def do_duplicate(self):
        self.total = sum(self.size_of(s) for s in self.sources)
        for s in self.sources:
            self.check()
            parent = s.get_parent()
            dst = parent.get_child(unique_name(parent, s.get_basename(), "copy", self.copy_word))
            self.created.append(dst)
            self.undo.append(("trash", dst))
            self.copy_one(s, dst)

    def do_restore(self):
        """Put items of the Trash back where they were (Mac: Put Back)."""
        for s in self.sources:
            self.check()
            info = s.query_info("trash::orig-path", NOFOLLOW, self.cancellable)
            orig = info.get_attribute_byte_string("trash::orig-path")
            if not orig:
                raise OpError(f"no original place for {s.get_basename()}")
            dst = Gio.File.new_for_path(orig)
            parent = dst.get_parent()
            if not exists(parent):
                parent.make_directory_with_parents(self.cancellable)
            if exists(dst):
                dst = parent.get_child(unique_name(parent, dst.get_basename()))
            s.move(dst, Gio.FileCopyFlags.NOFOLLOW_SYMLINKS, self.cancellable, None)
            self.created.append(dst)
            self.undo.append(("trash", dst))


def trash_item_for(orig_path, after=0):
    """The Trash item whose original place was orig_path (the most recent)."""
    trash = Gio.File.new_for_uri("trash:///")
    best, best_time = None, -1
    try:
        en = trash.enumerate_children("standard::name,trash::orig-path,trash::deletion-date", NOFOLLOW, None)
    except GLib.Error:
        return None
    for ci in en:
        if ci.get_attribute_byte_string("trash::orig-path") == orig_path:
            d = ci.get_deletion_date()
            t = d.to_unix() if d else 0
            if t >= after and t > best_time:
                best, best_time = trash.get_child(ci.get_name()), t
    en.close(None)
    return best


def move_back(a, b, cancellable=None):
    """Moves a to b; between two disks, a folder is copied and then removed
    (GIO cannot move a whole folder from one disk to another)."""
    try:
        a.move(b, Gio.FileCopyFlags.NOFOLLOW_SYMLINKS | Gio.FileCopyFlags.NO_FALLBACK_FOR_MOVE, cancellable, None)
        return
    except GLib.Error as e:
        if not (e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.NOT_SUPPORTED) or
                e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.WOULD_RECURSE)):
            raise
    j = Job("move", [], None)
    if cancellable is not None:
        j.cancellable = cancellable
    j.total = j.size_of(a)
    j.copy_one(a, b)
    j.delete_tree(a)


def undo(records, cancellable=None):
    """Undoes a finished job (its .undo list), last step first. Returns the errors."""
    errors = []
    for rec in reversed(records):
        try:
            if rec[0] == "move":              # moved src -> dst: move it back
                _, dst, src = rec
                if exists(src):
                    raise OpError(f"“{src.get_basename()}” is back in its place already")
                parent = src.get_parent()
                if not exists(parent):
                    parent.make_directory_with_parents(cancellable)
                move_back(dst, src, cancellable)
            elif rec[0] == "trash":           # created by us (copy, duplicate, new folder): to the Trash
                if exists(rec[1]):
                    try:
                        rec[1].trash(cancellable)
                    except GLib.Error as e:
                        if not e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.NOT_SUPPORTED):
                            raise
                        # a disk without Trash (USB stick...): it is a copy we just made, the
                        # original is still there, so removing it is what undo means
                        j = Job("delete", [], None)
                        if cancellable is not None:
                            j.cancellable = cancellable
                        j.delete_tree(rec[1])
            elif rec[0] == "untrash":         # trashed: put it back
                item = trash_item_for(rec[1])
                if item is None:
                    raise OpError(f"“{os.path.basename(rec[1])}” is no longer in the Trash")
                dst = Gio.File.new_for_path(rec[1])
                if exists(dst):
                    raise OpError(f"“{dst.get_basename()}” exists again")
                item.move(dst, Gio.FileCopyFlags.NOFOLLOW_SYMLINKS, cancellable, None)
            elif rec[0] == "rename":
                _, new, old = rec
                new.set_display_name(old, cancellable)
        except (GLib.Error, OpError) as e:
            errors.append(getattr(e, "message", str(e)))
    return errors
