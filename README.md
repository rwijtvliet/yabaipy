# Yabai-Py

Package to allow accessing yabai window manager using python by wrapping around the yabai API.

## Assumptions

Several assumptions are made in this package:

- Spaces can move around but (after initial setup) keep their labels.

- Spaces labels are unique, and distinct from other possible `SPACE_SEL` identifiers (such as integer numbers or words such as 'prev', 'next', 'first', etc.)
