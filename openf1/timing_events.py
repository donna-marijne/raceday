from datetime import datetime, timedelta

import log
import model
from openf1 import json_validation
from openf1.openf1_payload import JSONDict, JSONValue, OpenF1Payload


def timing_events_from_api(
    payload: OpenF1Payload,
    cars: dict[int, model.Car],
    stints: dict[int, list[model.Stint]],
):
    """Returns a list of TimingEvents ordered by timestamp"""

    timing_events: list[model.TimingEvent] = []
    for lap in payload.laps:
        date_start = json_validation.to_optional_datetime(lap["date_start"])
        duration_sector_1 = json_validation.to_optional_float(lap["duration_sector_1"])
        duration_sector_2 = json_validation.to_optional_float(lap["duration_sector_2"])
        duration_sector_3 = json_validation.to_optional_float(lap["duration_sector_3"])
        lap_duration = json_validation.to_optional_float(lap["lap_duration"])
        driver_number = json_validation.to_int(lap["driver_number"])
        lap_number = json_validation.to_int(lap["lap_number"])

        car = cars[driver_number]

        if date_start is None:
            # potentially a DNS
            log.debug(f"date_start is None: {lap}")
            continue

        stint = _active_stint(stints=stints, car_number=car.number, lap=lap_number)

        last_end = date_start
        sector_durations = _fixup_sector_durations(
            lap_duration, duration_sector_1, duration_sector_2, duration_sector_3
        )
        for i, duration in enumerate(sector_durations):
            if duration is None:
                log.debug(f"duration_sector_{i} is None: {lap}")
                continue

            if i == 2:
                stint = _active_stint(
                    stints=stints, car_number=car.number, lap=lap_number + 1
                )

            sector_end = last_end + timedelta(seconds=duration)

            sector = model.Sector(lap_number, i + 1)

            tyre_age = lap_number - stint.tyre_age_at_start

            car_state = model.CarState(
                number=car.number,
                position=-1,  # calculate later
                tyre_age=tyre_age,
                tyre_compound=stint.tyre_compound,
            )

            sector = model.TimingEvent(
                timestamp=sector_end,
                sector=sector,
                sector_duration=None,
                car=car,
                car_state=car_state,
            )

            timing_events.append(sector)

            last_end = sector_end

    timing_events = sorted(timing_events, key=lambda t: t.timestamp)

    # calculate positions and sector durations
    positions_by_sector = {}
    prev_event_by_car: dict[int, model.TimingEvent] = {}
    for timing_event in timing_events:
        # calculate car position in this sector
        sector = timing_event.sector
        if sector not in positions_by_sector:
            positions_by_sector[sector] = []
        positions_by_sector[sector].append(timing_event.car)
        timing_event.car_state.position = len(positions_by_sector[sector])

        # calculate sector durations
        car_number = timing_event.car.number
        if car_number in prev_event_by_car:
            prev_event = prev_event_by_car[car_number]
            prev_event.sector_duration = timing_event.timestamp - prev_event.timestamp
        prev_event_by_car[car_number] = timing_event

    return timing_events


def _fixup_sector_durations(
    lap_duration, duration_sector_1, duration_sector_2, duration_sector_3
):
    durations = [duration_sector_1, duration_sector_2, duration_sector_3]

    if lap_duration is None:
        # car retired, nothing to do
        return durations

    durations_total = 0.0
    missing_sector = None
    for i, duration in enumerate(durations):
        if duration is not None:
            durations_total += duration
            continue

        if missing_sector is not None:
            raise Exception(f"Lap completed with more than one missing sector")

        missing_sector = i

    if missing_sector is not None:
        # here we have one missing sector time and a lap_duration
        # so we can infill the difference
        durations[missing_sector] = lap_duration - durations_total

    return durations


def _active_stint(
    stints: dict[int, list[model.Stint]], car_number: int, lap: int
) -> model.Stint:
    assert car_number in stints
    for stint in reversed(stints[car_number]):
        if stint.lap_start <= lap:
            log.debug(
                f"found active stint {stint} in {stints[car_number]} for car {car_number}"
            )
            return stint

    raise Exception(
        f"no stint found for car {car_number} on lap {lap} in {stints[car_number]}"
    )
