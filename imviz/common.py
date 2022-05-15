"""
This contains common and (mostly) helpful utils.
"""

import os
import time
import pickle
import inspect
import hashlib
import traceback
import subprocess

import __main__

from contextlib import contextmanager

from imviz.autoreload import ModuleReloader

import imviz as viz


class bundle(dict):
    """
    A dict, which allows dot notation access.
    """

    def __init__(self, *args, **kwargs):

        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

    def __setstate__(self, state):

        self.update(state)


STATICS = {}
"""
Contains all static function variables.
"""


def statics(**defaults):
    """
    This (kind of) emulates the behavior of c++ static function variables.

    It returns a bundle, which is unique to the calling function.
    Like static variables the bundle is persisted between function calls.

    Use with caution! This implementation is probably not very performant,
    but really useful for quick-and-dirty experimentation.
    """

    caller = inspect.stack()[1]
    func_id = hash(caller.filename + caller.function)

    try:
        sts = STATICS[func_id]
        sts = bundle({**defaults, **sts})
        STATICS[func_id] = sts
    except KeyError:
        sts = bundle(defaults)
        STATICS[func_id] = sts

    return sts


RELOADER = None
"""
Contains a global module reloader for easier access.
"""


def update_autoreload():
    """
    This checks all used python modules for changes (mtime), reloads
    the respective code, and updates existing code as far as possible.

    The "__main__" module cannot be reloaded due to python limitations.

    As this uses asynchronous modification scanning, the function
    must be called repeatedly in the main application loop.

    Returns True if at least one module was sucessfully reloaded.
    Returns False otherwise.
    """

    global RELOADER

    if RELOADER is None:
        RELOADER = ModuleReloader()

    return RELOADER.reload()


@contextmanager
def error_sink():
    """
    This contextmanager catches and visualizes exceptions in the gui,
    instead of handing them over to the caller.
    """

    try:
        yield
    except Exception as e:
        viz.text(f"{type(e).__name__}: {e}", color=(1, 0, 0))
        if viz.is_item_hovered():
            viz.begin_tooltip()
            viz.text(f"{traceback.format_exc(-1)}")
            viz.end_tooltip()


AUTOSAVE_REQ = {}
AUTOSAVE_TIME = {}


@contextmanager
def autosave(obj, path=".imviz_save", timeout=0.5):

    if path not in AUTOSAVE_REQ:
        AUTOSAVE_REQ[path] = False
    if path not in AUTOSAVE_TIME:
        AUTOSAVE_TIME[path] = -1

    if AUTOSAVE_TIME[path] < 0:
        viz.storage.load(obj, path)
        AUTOSAVE_TIME[path] = time.time()

    viz.push_mod_any()

    yield

    if viz.pop_mod_any():
        AUTOSAVE_REQ[path] = True
        AUTOSAVE_TIME[path] = time.time()

    if AUTOSAVE_REQ[path] and (time.time() - AUTOSAVE_TIME[path]) > timeout:
        AUTOSAVE_REQ[path] = False
        viz.storage.save(obj, path)


LATEX_IMG_CACHE = {}

if hasattr(__main__, "__file__"):
    wd = os.path.abspath(os.path.dirname(__main__.__file__))
else:
    wd = os.getcwd()

LATEX_CACHE_DIR = os.path.join(wd, "__pycache__", "latex")
os.makedirs(LATEX_CACHE_DIR, exist_ok=True)


def latex(text, dpi=120):

    hasher = hashlib.sha1()
    hasher.update((text + str(dpi)).encode("utf8"))
    text_hash = hasher.hexdigest()

    latex_img = None

    if text_hash in LATEX_IMG_CACHE:
        latex_img = LATEX_IMG_CACHE[text_hash]
    else:
        tmpl_path = os.path.join(LATEX_CACHE_DIR, "lt.tex")
        with open(tmpl_path, "w+") as fd:
            fd.write(r"\documentclass[12pt]{standalone} \begin{document} "
                     + text
                     + r" \end{document}")

        proc = subprocess.run("latex -halt-on-error -interaction=nonstopmode "
                              + "lt.tex "
                              + f"&& dvipng -D {dpi} lt.dvi -o res.png",
                              shell=True,
                              cwd=LATEX_CACHE_DIR,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        if proc.returncode == 0:
            latex_img = viz.load_image(
                    os.path.join(LATEX_CACHE_DIR, "res.png"))
            latex_img = 255 - latex_img
            LATEX_IMG_CACHE[text_hash] = latex_img
        else:
            print(proc.stdout.decode("utf8") + "\n\n")
            raise RuntimeError("Latex error: see console for details")

    if latex_img is not None:
        viz.image(text_hash, latex_img)


class Selection():
    """
    This class combines a combo box selection with a list of options.
    """

    def __init__(self, options=[], index=0):

        self.options = options
        self.index = 0

    def __autogui__(self, name, **kwargs):

        self.index = viz.combo(name, self.options, self.index)
        viz.same_line()
        self.options = viz.autogui(
                self.options, f"###{name}_options")

        return self

    def selected(self):

        try:
            return self.options[self.index]
        except IndexError:
            return None


class ModHistory:

    mod_counter = 0

    def __init__(self):

        self.pos = -1
        self.history = []
        self.time = 0
        self.save_req = False

    def save(self, obj):

        ModHistory.mod_counter += 1
        if self.pos < len(self.history) - 1:
            self.history = self.history[:self.pos - len(self.history) + 1]
        self.history.append((ModHistory.mod_counter, pickle.dumps(obj)))
        self.pos += 1

    def get_undo_id(self):

        if self.pos - 1 >= 0:
            return self.history[self.pos][0]
        else:
            return 0

    def get_undo_state(self):

        if self.pos - 1 >= 0:
            return pickle.loads(self.history[self.pos-1][1])
        else:
            return None

    def get_redo_id(self):

        if self.pos + 1 <= len(self.history) - 1:
            return self.history[self.pos][0]
        else:
            return 0

    def get_redo_state(self):

        if self.pos + 1 <= len(self.history) - 1:
            return pickle.loads(self.history[self.pos+1][1])
        else:
            return None


MOD_HISTORIES = {}
UNDO_CANDIDATE = None
REDO_CANDIDATE = None


@contextmanager
def mod_history(name, obj, timeout=0.5):

    global UNDO_CANDIDATE
    global REDO_CANDIDATE

    hist_id = viz.get_id(name)

    try:
        hist = MOD_HISTORIES[hist_id]
    except KeyError:
        hist = ModHistory()
        hist.save(obj)
        MOD_HISTORIES[hist_id] = hist

    if UNDO_CANDIDATE == hist:
        obj = hist.get_undo_state()
        hist.pos -= 1
        UNDO_CANDIDATE = None
        viz.set_mod(True)

    if REDO_CANDIDATE == hist:
        obj = hist.get_redo_state()
        hist.pos += 1
        REDO_CANDIDATE = None
        viz.set_mod(True)

    for ke in viz.get_key_events():
        if ke.action == viz.RELEASE:
            continue
        if ke.mod != viz.MOD_CONTROL:
            continue
        if ke.key == viz.KEY_Y:
            if hist.get_redo_id() == 0:
                break
            if REDO_CANDIDATE is None:
                REDO_CANDIDATE = hist
                break
            if REDO_CANDIDATE.get_redo_id() > hist.get_redo_id():
                REDO_CANDIDATE = hist
                break
        if ke.key == viz.KEY_Z:
            if hist.get_undo_id() == 0:
                break
            if UNDO_CANDIDATE is None:
                UNDO_CANDIDATE = hist
                break
            if UNDO_CANDIDATE.get_undo_id() < hist.get_undo_id():
                UNDO_CANDIDATE = hist
                break

    viz.push_mod_any()

    yield obj

    if viz.pop_mod_any():
        hist.save_req = True
        hist.time = time.time()

    if hist.save_req and (time.time() - hist.time) > timeout:
        hist.save_req = False
        hist.save(obj)
