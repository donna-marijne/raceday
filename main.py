import argparse
import curses
import json
from dataclasses import asdict
from pathlib import Path

import model
import simulator
import tui
from datetime_json_encoder import DateTimeJSONEncoder
from event_loop import event_loop
from handle_input import handle_input
from openf1.session import session_from_source_dir


def curses_main(stdscr: curses.window):
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
    parser.add_argument(
        "-f",
        "--frequency",
        type=int,
        default=30,
        help="update frequency (per second)",
    )

    args = parser.parse_args()

    session = init_session(args)
    debug_session(session)

    sim = simulator.Simulator(session=session)

    app = tui.App(window=stdscr, state=sim.state)
    app.first_render()

    input_handler = lambda: handle_input(stdscr)

    event_loop(
        sim=sim,
        input_callback=input_handler,
        frame_callback=app.update,
        time_warp=args.time_warp,
        frequency=args.frequency,
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


def debug_session(session: model.Session):
    timing_events_json = json.dumps(
        [asdict(te) for te in session.timing_events], cls=DateTimeJSONEncoder
    )
    with open("timing_events.json", "w") as file:
        file.write(timing_events_json)


if __name__ == "__main__":
    curses.wrapper(curses_main)
