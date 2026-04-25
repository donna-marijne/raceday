import argparse

from event_loop import event_loop
from openf1.timing_events import timing_events_from_source_dir


def main():
    print("Hello from raceday!")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--source-dir",
        help="run offline using OpenF1 JSON files in the specified directory",
    )

    args = parser.parse_args()

    timing_events = []
    if args.source_dir:
        print("offline mode!")
        print(args.source_dir)
        timing_events = timing_events_from_source_dir(args.source_dir)
    else:
        print("online mode!")

    event_loop(timing_events, callback=print_timing_event, time_warp=10)

    print("That's the chequered flag for this program!")


def print_timing_event(timing_event):
    print(
        f"Car {timing_event.car.number} completes lap {timing_event.sector.lap} sector {timing_event.sector.sector} in P{timing_event.car_position} at {timing_event.timestamp}"
    )


if __name__ == "__main__":
    main()
