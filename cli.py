#!/usr/bin/env python
"""Command-line interface of the package."""

import yabaipy as yp

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Wrapper around yabai commands to keep things in order."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands.")

    send_to_display = subparsers.add_parser(
        "send_to_display",
        help="Send current space to a display while maintaining correct space order on the display.",
    )
    send_to_display.add_argument("display_sel", type=str, help="Display to send it to")

    sort_display = subparsers.add_parser(
        "sort_display", help="Sort spaces on a display."
    )
    sort_display.add_argument(
        "display_sel", type=str, nargs="?", help="Display to sort the spaces of"
    )

    sort_displays = subparsers.add_parser(
        "sort_displays", help="Sort spaces on all displays."
    )

    args = parser.parse_args()
    if args.command == "send_to_display":
        print(f"Sending current space to display {args.display_sel}.")
        yp.send_space_to_display(None, args.display_sel)
    elif args.command == "sort_display":
        print(f"Sorting spaces on display {args.display_sel}.")
        yp.sort_display(args.display_sel)
    elif args.command == "sort_displays":
        print("Sorting spaces on all displays.")
        yp.sort_displays()
    else:
        print("doing nothing")


if __name__ == "__main__":
    main()
