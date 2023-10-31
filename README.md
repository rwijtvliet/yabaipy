# yabpy

Package to access [yabai](https://github.com/koekeishiya/yabai/tree/master) window manager using python by wrapping around the yabai API.

It works with yabai 6.

## Installation

```bash
poetry install
```

Creates a virtual environment in `.venv/` and makes the command line tool available at `.venv/bin/yabpy`. This file can be symlinked to a location on your path (e.g. `/usr/local/bin/`) so that the cli is available from the command line.

## Usage

```python
import yabpy as yp

sp = yp.Space('1_files')
sp.send_to_display('west')
sp.get_display().sort()
```

or, from the terminal:

```bash
path/to/repository/.venv/bin/yabpy space-to-display west
```

The cli exposes higher-level functionality only. For all commands, use `yabpy --help`.

The cli can be used in the `shkdrc` file to be triggered on keyboard shortcuts.

## Issues solved by this package

The main issue for me was: when moving a space to another display, the order is not always respected. If I move space `'2_www'` onto the same display as `'1_files'` and `'3_terminal'`, I want it to be inserted between them. This package solves that by adding a `.sort()` method to the `Display` class. From the command line interface, the sorting can be triggered manually. Also, when moving a space using the command line interface, the sorting is done afterwards.

Also, a `SpaceDef` class and acompanying `spaces.json` file are introduced. These allow specifying additional properties on spaces, such as the preferred display. This is used when preparing the spaces and can be called when a display is added.

Minor additional things:

- A notification is shown on some commands.

## Package details

The package defines classes `Window`, `Space`, and `Display`, which can be instantiated with a yabai selector as defined in its [documentation](https://github.com/koekeishiya/yabai/blob/master/doc/yabai.asciidoc#5-definitions).

- The reference to a specific object, e.g. a space, is retained, even if the space is change, relabelled, or moved to a different display. For example, `sp = Space()` gets a reference to the currently focused space. If the space is moved to another display, or another position in the mission control order, or is no longer focused, `sp` still references that same space.

- The up-to-date object properties can be accessed through `.props()`, which returns a dataclass with relevant data as specified [here](https://github.com/koekeishiya/yabai/blob/master/doc/yabai.asciidoc#654-dataformat) - with minor changes in the property names to stay complient with python.

Other parts of the API, e.g. setting rules, are not currently implemented.

## Unsolved issues

- When moving/refocusing a space, the focus often moves to a different app or window. I currently suspect this is due to an issue with Microsoft Teams (which is what gets the focus), and am observing if quitting it resolves the issue. Also, the issue seems resolved with the latest Teams version. Regardless, this packages can be used to get a reference to the active window before making the change, and refocus the window afterwards. This is not currently implemented in the command line interface.

- (Re)starting yabai: when starting yabai, the label a space previously had is lost. I assign labels by looping through the spaces, but if they were in order `'1_files'`, `'3_terminal'`, `'2_www'`, they will be uncorrectly relabeled `'1_files'`, `'2_www'`, `'3_terminal'`. This issue is not solved by this package.

## Future work

I'm not sure where I want to take this package. It was written out of necessity, but it is a bit overkill for my purposes, and changes in the `yabai` API mean that this will likely break in the future. Ideally - at least, for me ;) - the relevant functionality (in `yabpy/additional.py` and/or `yabpy/cli.py`, mainly; some functionality also in the classes) is absorbed into yabai itself at some point.
