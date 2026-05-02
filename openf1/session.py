from datetime import datetime
from zoneinfo import ZoneInfo

import log
from car import Car
from openf1.openf1_payload import OpenF1Payload
from openf1.timing_events import timing_events_from_api_laps
from session import Session


def session_from_source_dir(dir_path):
    return _session_from_api(OpenF1Payload.from_source_dir(dir_path))


def _session_from_api(payload: OpenF1Payload):
    if len(payload.drivers) == 0:
        raise ValueError(f"unexpectedly saw {len(payload.drivers)} drivers")

    if len(payload.starting_grid) == 0:
        raise ValueError(f"unexpectedly saw {len(payload.starting_grid)} starting_grid")

    if len(payload.laps) == 0:
        raise ValueError(f"unexpectedly saw {len(payload.laps)} laps")

    start = _session_start_from_api(payload)
    cars = _cars_from_api(payload.drivers)
    starting_grid = _starting_grid_from_api(payload.starting_grid, cars)
    timing_events = timing_events_from_api_laps(payload.laps, cars)
    total_laps = _total_laps(timing_events)

    return Session(
        name=f"{payload.meeting['year']} {payload.meeting['meeting_name']}",
        start=start,
        total_laps=total_laps,
        cars=cars,
        starting_grid=starting_grid,
        timing_events=timing_events,
    )


def _session_start_from_api(payload: OpenF1Payload) -> datetime:
    # TODO: replace with race control event when available
    laps = payload.laps
    start = None
    for lap in laps:
        date_start = lap["date_start"]
        if date_start is None:
            continue

        lap_start = datetime.fromisoformat(str(date_start))
        if start is None:
            start = lap_start
        else:
            start = min(start, lap_start)

    assert start is not None
    return start


def _cars_from_api(drivers):
    cars = {}
    for driver in drivers:
        cars[driver["driver_number"]] = Car(
            number=driver["driver_number"],
            driver_name=driver["full_name"],
            driver_acronym=driver["name_acronym"],
            team_name=driver["team_name"],
            color=driver["team_colour"],
        )

    return cars


def _starting_grid_from_api(starting_grid, cars):
    grid = []
    for grid_slot in starting_grid:
        position = grid_slot["position"]
        driver_number = grid_slot["driver_number"]

        if driver_number not in cars:
            raise ValueError(
                f"driver_number {driver_number} in starting_grid but not drivers"
            )

        # grid slots may be empty or out of order
        if position > len(grid):
            grid.extend([None] * (position - len(grid)))

        grid[position - 1] = cars[driver_number]

    return grid


def _total_laps(timing_events):
    total_laps = 0
    for timing_event in timing_events:
        total_laps = max(total_laps, timing_event.sector.lap)
    return total_laps
