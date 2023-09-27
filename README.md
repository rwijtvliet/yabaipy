# Yabai-Py

Package to access yabai window manager using python by wrapping around the yabai API.

## Assumptions

Several assumptions are made in this package:

- Spaces can move around and their labels can change.

- If a space has a (non-empty-string) label, it is unique, and does not collide with other possible `SPACE_SEL` identifiers (such as integer numbers or words such as 'prev', 'next', 'first', etc.)

The latter point is enforced when using the package whenever an unlabeled space is labeled.

## What this package solves

Issues with `yabai`:

- When starting yabai, I cannot access the label a space previously had. I assign labels by looping through the spaces, but if they were in order `'one'`, `'three'`, `'two'`, they will be uncorrectly relabeled `'one'`, `'two'`, `'three'`.

- When moving a space to another display, the order is not always respected. If I move space `'two'` onto the same display as `'one'`, I want it to be inserted after `'one'`.

-

## Functionality / Use cases

### Configuration

Initially, the wanted order of the spaces and their preferred monitor are configured.

```
config = [
    {'label': '1_files', 'icon': '', 'display': 1}
    {'label': '2_www', 'icon': '', 'display': 2}
    {'label': '3_terminal', 'icon': '', 'display': 1}
    {'label': '4_email', 'icon': '', 'display': 3}
]
```

Remarks:

- There must be at least one space for each display that _might_ be connected.

  E.g. the config above cannot be used on a setup with 4 or more displays.

- If not enough displays: spaces are moved to last display.

  E.g. if the config above is used with 2 displays, space '4_email' is shown on display with arrangement index 2.

-
