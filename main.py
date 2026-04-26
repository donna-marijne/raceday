import argparse
import curses

from curses_renderer import CursesRenderer
from event_loop import event_loop
from openf1.timing_events import timing_events_from_source_dir


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

    timing_events = init_timing_events(args)

    renderer = CursesRenderer(stdscr)
    renderer.render_ui()

    event_loop(
        timing_events,
        callback=renderer.render_timing_event,
        time_warp=args.time_warp,
    )


def init_timing_events(args):
    timing_events = []
    if args.source_dir:
        print("offline mode!")
        print(args.source_dir)
        timing_events = timing_events_from_source_dir(args.source_dir)
    else:
        print("online mode!")

    return timing_events


if __name__ == "__main__":
    curses.wrapper(curses_main)
