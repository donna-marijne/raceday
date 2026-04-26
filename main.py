import argparse
import curses
import os
from pathlib import Path

from curses_renderer import CursesRenderer
from event_loop import event_loop
from openf1.session import session_from_source_dir


def curses_main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--source-dir",
        help="run offline using OpenF1 JSON files in the specified directory",
    )
    parser.add_argument(
        "-w",
        "--time-warp",
        type=int,
        default=10,
        help="time multiplier to use when replaying",
    )

    args = parser.parse_args()

    session = init_session(args)

    renderer = CursesRenderer(stdscr, session)
    renderer.render_ui()

    event_loop(
        session.timing_events,
        callback=renderer.render_timing_event,
        time_warp=args.time_warp,
    )


def init_session(args):
    source_dir = Path(args.source_dir)
    session = None
    if args.source_dir:
        session = session_from_source_dir(source_dir)
    else:
        print("online mode!")

    return session


if __name__ == "__main__":
    curses.wrapper(curses_main)
