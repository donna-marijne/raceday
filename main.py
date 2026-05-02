import argparse
import curses
import json
from dataclasses import asdict
from pathlib import Path

import log
from curses_renderer import CursesRenderer
from datetime_json_encoder import DateTimeJSONEncoder
from event_loop import event_loop
from openf1.session import session_from_source_dir
from session import Session


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
    debug_session(session)

    renderer = CursesRenderer(stdscr, session)
    renderer.render_ui()

    event_loop(
        session,
        event_callback=renderer.render_timing_event,
        time_callback=renderer.render_clock,
        time_warp=args.time_warp,
    )


def init_session(args):
    source_dir = Path(args.source_dir)
    session = None
    if args.source_dir:
        session = session_from_source_dir(source_dir)
    else:
        print("online mode!")
        raise NotImplementedError("online mode tbd")

    return session


def debug_session(session: Session):
    timing_events_json = json.dumps(
        [asdict(te) for te in session.timing_events], cls=DateTimeJSONEncoder
    )
    with open("timing_events.json", "w") as file:
        file.write(timing_events_json)


if __name__ == "__main__":
    curses.wrapper(curses_main)
