import json

from car import Car
from openf1.timing_events import timing_events_from_api_laps
from session import Session


def session_from_source_dir(dir_path):
    sessions = None
    with (dir_path / "sessions.json").open("r") as sessions_file:
        json_str = sessions_file.read()
        sessions = json.loads(json_str)
    drivers = None
    with (dir_path / "drivers.json").open("r") as drivers_file:
        json_str = drivers_file.read()
        drivers = json.loads(json_str)
    starting_grid = None
    with (dir_path / "starting_grid.json").open("r") as starting_grid_file:
        json_str = starting_grid_file.read()
        starting_grid = json.loads(json_str)
    laps = None
    with (dir_path / "laps.json").open("r") as laps_file:
        json_str = laps_file.read()
        laps = json.loads(json_str)

    return session_from_json(
        sessions=sessions,
        drivers=drivers,
        starting_grid=starting_grid,
        laps=laps,
    )


def session_from_json(sessions, drivers, starting_grid, laps):
    if len(sessions) != 1:
        raise ValueError(f"unexpectedly saw {len(sessions)} sessions")

    session = sessions[0]

    if len(drivers) == 0:
        raise ValueError(f"unexpectedly saw {len(drivers)} drivers")

    if len(starting_grid) == 0:
        raise ValueError(f"unexpectedly saw {len(starting_grid)} starting_grid")

    if len(laps) == 0:
        raise ValueError(f"unexpectedly saw {len(laps)} laps")

    cars = _cars_from_api(drivers)
    grid = _starting_grid_from_api(starting_grid, cars)
    timing_events = timing_events_from_api_laps(laps, cars)
    total_laps = _total_laps(timing_events)

    return Session(
        name=f"{session['year']} {session['country_name']}",
        total_laps=total_laps,
        cars=cars,
        starting_grid=grid,
        timing_events=timing_events,
    )


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
