"""Shared functionality."""

import subprocess


def run_bash(command: str) -> str:
    """Run command in subprocess, returning the result if successful."""
    result = subprocess.run(
        command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.decode("utf-8"))
    return result.stdout.decode("utf-8")


def run_osascript(command: str):
    result = subprocess.run(["osascript", "-e", command], capture_output=True)
    if result.returncode != 0:
        raise ValueError(result.stderr.decode("utf-8"))
    return result.stdout.decode("utf-8")


def notify(msg: str, *, title: str = None):
    t = f'with title "{title}"' if title is not None else ""
    run_osascript(f'display notification "{msg}" {t}')
