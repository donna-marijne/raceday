from datetime import datetime, timedelta

import log
import model
from openf1.openf1_payload import JSONValue, OpenF1Payload


def timing_events_from_api(payload: OpenF1Payload, cars: dict[int, model.Car]):
    """Returns a list of TimingEvents ordered by timestamp"""

    laps = payload.laps

    timing_events: list[model.TimingEvent] = []
    for lap in laps:
        date_start = _datetime_from_json(lap["date_start"])
        duration_sector_1 = _float_from_json(lap["duration_sector_1"])
        duration_sector_2 = _float_from_json(lap["duration_sector_2"])
        duration_sector_3 = _float_from_json(lap["duration_sector_3"])
        lap_duration = _float_from_json(lap["lap_duration"])
        driver_number = _int_from_json(lap["driver_number"])
        lap_number = _int_from_json(lap["lap_number"])

        if driver_number is None:
            raise ValueError(f"driver_number is None: {lap}")

        if lap_number is None:
            raise ValueError(f"lap_number is None: {lap}")

        car = cars[driver_number]

        if date_start is None:
            # potentially a DNS
            log.debug(f"date_start is None: {lap}")
            continue

        last_end = date_start
        sector_durations = _fixup_sector_durations(
            lap_duration, duration_sector_1, duration_sector_2, duration_sector_3
        )
        for i, duration in enumerate(sector_durations):
            if duration is None:
                log.debug(f"duration_sector_{i} is None: {lap}")
                continue

            sector_end = last_end + timedelta(seconds=duration)

            sector = model.Sector(lap_number, i + 1)

            car_state = model.CarState(
                position=-1,  # calculate later
                tyre_age=1,
                tyre_compound=model.TyreCompound.HARD,
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


def _datetime_from_json(json: JSONValue) -> datetime | None:
    if json is None:
        return None
    return datetime.fromisoformat(str(json))


def _int_from_json(json: JSONValue) -> int | None:
    if json is None:
        return None
    return int(json)


def _float_from_json(json: JSONValue) -> float | None:
    if json is None:
        return None
    return float(json)
