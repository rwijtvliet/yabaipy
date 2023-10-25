# yabpy

Package to access [yabai](https://github.com/koekeishiya/yabai/tree/master) window manager using python by wrapping around the yabai API.

It works with yabai 6.

## Assumptions

Several assumptions are made in this package:

- Spaces can move around (to different displays) and their labels can change.

- On each display, the spaces should be sorted by their label.

- If a space has a (non-empty-string) label, it is unique, and does not collide with other possible `SPACE_SEL` identifiers (such as integer numbers or words such as 'prev', 'next', 'first', etc.)

The latter point is enforced when using the package to label an unlabeled space.

## Issues with yabai

- (Re)starting yabai: when starting yabai, the label a space previously had is lost. I assign labels by looping through the spaces, but if they were in order `'1_files'`, `'3_terminal'`, `'2_www'`, they will be uncorrectly relabeled `'1_files'`, `'2_www'`, `'3_terminal'`. This issue is not solved by this package.

- When moving a space to another display, the order is not always respected. If I move space `'2_www'` onto the same display as `'1_files'` and `'3_terminal'`, I want it to be inserted between them. This package solves that by adding a `.sort()` method to the `Display` class. From the command line interface, the sorting can be triggered manually. Also, when moving a space using the command line interface, the sorting is done afterwards.

- When moving/refocusing a space, the focus often moves to a different app or window. I currently suspect this is due to an issue with Microsoft Teams (which is what gets the focus), and am observing if quitting it resolves the issue. Also, the issue seems resolved with the latest Teams version. Regardless, this packages can be used to get a reference to the active window before making the change, and refocus the window afterwards. This is not currently implemented in the command line interface.

## Package details

The package defines classes `Window`, `Space`, and `Display`, which can be instantiated with a yabai selector as defined in its [documentation](https://github.com/koekeishiya/yabai/blob/master/doc/yabai.asciidoc#5-definitions).

- The reference to a specific object, e.g. a space, is retained, even if the space is change, relabelled, or moved to a different display. For example, `sp = Space()` gets a reference to the currently focused space. If the space is moved to another display, or another position in the mission control order, or is no longer focused, `sp` still references that same space.

- The up-to-date object properties can be accessed through `.props()`, which returns a dataclass with relevant data as specified [here](https://github.com/koekeishiya/yabai/blob/master/doc/yabai.asciidoc#654-dataformat) - with minor changes to stay complient with python.

Other parts of the API, e.g. setting rules, are not currently implemented.

## Usage

```python
import yabpy as yp

sp = yp.Space('1_files')
sp.send_to_display('west')
sp.get_display().sort()
```

or, from the cli:

```bash
./cli.py send_to_display west
```

The cli exposes higher-level functionality only. Under the hood, the `send_to_display` command calls the `Space.send_to_display()` and the `Display.sort()` methods. For all cli commands, use `./cli.py --help`.

## Future work

I'm not sure where I want to take this package. It was written out of necessity, but it is a bit overkill for my purposes, and changes in the `yabai` API mean that this will likely break in the future. Ideally - at least, for me ;) - the relevant functionality (in `/yabpy/additional.py`, mainly; some functionality also in the classes) is absorbed into yabai itself at some point.
