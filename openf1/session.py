from datetime import datetime, timedelta
from typing import Tuple

import model
from model.tyre_compound import TyreCompound
from openf1 import json_validation
from openf1.openf1_payload import OpenF1Payload
from openf1.timing_events import timing_events_from_api


def session_from_source_dir(dir_path):
    return _session_from_api(OpenF1Payload.from_source_dir(dir_path))


def _session_from_api(payload: OpenF1Payload):
    start = _session_start_from_api(payload)
    quali_lap = _quali_lap_from_api(payload)
    sector_split = _sector_split_from_quali_lap(quali_lap)
    cars = _cars_from_api(payload.drivers)
    stints = _stints_from_api(payload)
    starting_grid = _starting_grid_from_api(payload, stints)
    pit_events_by_car = _pit_events_from_api(payload, cars=cars)
    timing_events = timing_events_from_api(payload, cars=cars)
    total_laps = _total_laps(timing_events)
    car_timing_events = _car_timing_events(timing_events)

    return model.Session(
        name=f"{payload.meeting['year']} {payload.meeting['meeting_name']}",
        start=start,
        sector_split=sector_split,
        total_laps=total_laps,
        cars=cars,
        starting_grid=starting_grid,
        stints=stints,
        pit_events_by_car=pit_events_by_car,
        timing_events=timing_events,
        timing_events_by_car=car_timing_events,
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


def _quali_lap_from_api(payload: OpenF1Payload) -> Tuple[float, float, float]:
    fastest_lap = float("inf")
    fastest_lap_sectors = None
    for lap in payload.qualifying_laps:
        lap_duration = json_validation.to_optional_float(lap["lap_duration"])
        if lap_duration is None or lap_duration >= fastest_lap:
            continue

        fastest_lap = lap_duration

        duration_sector_1 = json_validation.to_float(lap["duration_sector_1"])
        duration_sector_2 = json_validation.to_float(lap["duration_sector_2"])
        duration_sector_3 = json_validation.to_float(lap["duration_sector_3"])

        fastest_lap_sectors = (duration_sector_1, duration_sector_2, duration_sector_3)

    assert fastest_lap_sectors is not None

    return fastest_lap_sectors


def _stints_from_api(payload: OpenF1Payload) -> dict[int, list[model.Stint]]:
    """Returns the stints from the payload in a dict by car number and sorted in race order"""
    stints_map: dict[int, list[model.Stint]] = {}
    for stint_json in payload.stints:
        stint_number = json_validation.to_int(stint_json["stint_number"])
        driver_number = json_validation.to_int(stint_json["driver_number"])
        lap_start = json_validation.to_int(stint_json["lap_start"])
        compound = json_validation.to_str(stint_json["compound"])
        tyre_age_at_start = json_validation.to_int(stint_json["tyre_age_at_start"])

        stint = model.Stint(
            number=stint_number,
            car_number=driver_number,
            lap_start=lap_start,
            tyre_compound=TyreCompound[compound],
            tyre_age_at_start=tyre_age_at_start,
        )

        if driver_number not in stints_map:
            stints_map[driver_number] = []

        stints_map[driver_number].append(stint)

    for car_number in stints_map:
        stints_map[car_number] = sorted(stints_map[car_number], key=lambda s: s.number)

    return stints_map


def _cars_from_api(drivers):
    cars = {}
    for driver in drivers:
        cars[driver["driver_number"]] = model.Car(
            number=driver["driver_number"],
            driver_name=driver["full_name"],
            driver_acronym=driver["name_acronym"],
            team_name=driver["team_name"],
            color=driver["team_colour"],
        )

    return cars


def _pit_events_from_api(
    payload: OpenF1Payload, cars: dict[int, model.Car]
) -> dict[int, list[model.PitEvent]]:
    pit_events_by_car: dict[int, list[model.PitEvent]] = {}
    for car_number in cars:
        pit_events_by_car[car_number] = []

    for pit in payload.pit:
        date = json_validation.to_datetime(pit["date"])
        lane_duration = json_validation.to_float(pit["lane_duration"])
        driver_number = json_validation.to_int(pit["driver_number"])

        pit_event_in = model.PitEvent(
            car=cars[driver_number],
            in_lane=True,
            timestamp=date,
        )

        pit_event_out = model.PitEvent(
            car=cars[driver_number],
            in_lane=False,
            timestamp=date + timedelta(seconds=lane_duration),
        )

        pit_events_by_car[driver_number].extend([pit_event_in, pit_event_out])

    for pit_events in pit_events_by_car.values():
        pit_events.sort(key=lambda pit_event: pit_event.timestamp)

    return pit_events_by_car


def _starting_grid_from_api(
    payload: OpenF1Payload, stints: dict[int, list[model.Stint]]
) -> list[int]:
    grid = []
    for grid_slot in payload.starting_grid:
        position = json_validation.to_int(grid_slot["position"])
        driver_number = json_validation.to_int(grid_slot["driver_number"])

        # grid slots may be empty or out of order
        if position > len(grid):
            grid.extend([None] * (position - len(grid)))

        if driver_number not in stints:
            raise Exception(f"car {driver_number} in starting_grid but not in stints")

        grid[position - 1] = driver_number

    return grid


def _total_laps(timing_events):
    total_laps = 0
    for timing_event in timing_events:
        total_laps = max(total_laps, timing_event.sector.lap)
    return total_laps


def _car_timing_events(
    timing_events: list[model.TimingEvent],
) -> dict[int, list[model.TimingEvent]]:
    car_timing_events = {}
    for timing_event in timing_events:
        car = timing_event.car.number
        if car not in car_timing_events:
            car_timing_events[car] = []
        car_timing_events[car].append(timing_event)

    return car_timing_events


def _sector_split_from_quali_lap(
    lap_sectors: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    total = lap_sectors[0] + lap_sectors[1] + lap_sectors[2]

    return (
        (lap_sectors[0] / total),
        (lap_sectors[1] / total),
        (lap_sectors[2] / total),
    )
