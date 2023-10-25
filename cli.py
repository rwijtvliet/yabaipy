#!/usr/bin/env python
"""Command-line interface of the package."""

import yabpy as yp

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Wrapper around yabai commands to keep things in order."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands.")

    # send to display
    send_to_display = subparsers.add_parser(
        "send_to_display",
        help="Send current space to a display while maintaining correct space order on the display.",
    )
    send_to_display.add_argument("display_sel", type=str, help="Display.")

    # sort display
    sort_display = subparsers.add_parser(
        "sort_display", help="Sort spaces on a display."
    )
    sort_display.add_argument(
        "display_sel",
        type=str,
        nargs="?",
        help="Display (omit to use current display).",
    )

    # sort all displays
    sort_displays = subparsers.add_parser(
        "sort_displays", help="Sort spaces on all displays."
    )

    # assert sorted
    assert_sorted = subparsers.add_parser(
        "assert_sorted", help="Assert spaces on all displays are sorted."
    )

    # Do the actual work
    args = parser.parse_args()
    if args.command == "send_to_display":
        print(f"Sending current space to display {args.display_sel}.")
        yp.send_space_to_display(None, args.display_sel)

    elif args.command == "sort_display":
        print(f"Sorting spaces on display {args.display_sel}.")
        yp.Display(args.display_sel).sort()

    elif args.command == "sort_displays":
        for di in yp.get_all_displays():
            print(f"Sorting spaces on display {di.props().index}.")
            di.sort()

    elif args.command == "assert_sorted":
        for di in yp.get_all_displays():
            print(f"Asserting if spaces are sorted on display {di.props().index}.")
            try:
                yp.assert_display_sorted(di)
            except AssertionError as e:
                print(f"Spaces are not sorted.\n{e.args[0]}")
            else:
                print("Spaces are sorted.")

    else:
        print("doing nothing")


if __name__ == "__main__":
    main()
