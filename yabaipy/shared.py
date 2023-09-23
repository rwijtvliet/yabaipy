from typing import Callable, Any
import subprocess


def none_not_allowed(fn: Callable):
    def wrapped(sel: Any = None, *args, **kwargs):
        if sel is None:
            raise ValueError("Must provide value")
        return fn(sel, *args, **kwargs)

    return wrapped


def none_means_current(fn: Callable):
    def wrapped(sel: Any = None, *args, **kwargs):
        if sel is None:
            sel = ""
        return fn(sel, *args, **kwargs)

    return wrapped


def assert_not_none(sel: Any):
    if sel is None:
        raise ValueError("Must provide a value; got None.")


def run_command(command: str):
    result = subprocess.run(
        command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.decode("utf-8"))
    return result.stdout.decode("utf-8")
