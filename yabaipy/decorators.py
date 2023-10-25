import functools
from . import displays, spaces, windows


def accept_display_instance(fn):
    @functools.wraps(fn)
    def wrapped(self, d, *args, **kwargs):
        if isinstance(d, displays.Display):
            return fn(self, d.display_sel, *args, **kwargs)
        return fn(self, d, *args, **kwargs)

    return wrapped


def accept_space_instance(fn):
    @functools.wraps(fn)
    def wrapped(self, s, *args, **kwargs):
        if isinstance(s, spaces.Space):
            return fn(self, s.space_sel, *args, **kwargs)
        return fn(self, s, *args, **kwargs)

    return wrapped


def accept_window_instance(fn):
    @functools.wraps(fn)
    def wrapped(self, w, *args, **kwargs):
        if isinstance(w, windows.Window):
            return fn(self, w.display_sel, *args, **kwargs)
        return fn(self, w, *args, **kwargs)

    return wrapped
