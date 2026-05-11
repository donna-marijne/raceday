from datetime import datetime, timedelta

import log
from car import Car
from sector import Sector
from timing_event import TimingEvent


def timing_events_from_api_laps(laps, cars: dict[int, Car]):
    """Returns a list of TimingEvents ordered by timestamp"""

    timing_events: list[TimingEvent] = []
    for lap in laps:
        date_start = lap["date_start"]
        duration_sector_1 = lap["duration_sector_1"]
        duration_sector_2 = lap["duration_sector_2"]
        duration_sector_3 = lap["duration_sector_3"]
        lap_duration = lap["lap_duration"]
        driver_number = lap["driver_number"]
        lap_number = lap["lap_number"]

        car = cars[driver_number]

        if date_start is None:
            log.debug(f"date_start is None: {lap}")
            continue

        last_end = datetime.fromisoformat(date_start)
        sector_durations = _fixup_sector_durations(
            lap_duration, duration_sector_1, duration_sector_2, duration_sector_3
        )
        for i, duration in enumerate(sector_durations):
            if duration == None:
                log.debug(f"duration_sector_{i} is None: {lap}")
                continue

            sector_end = last_end + timedelta(seconds=duration)

            sector = Sector(lap_number, i + 1)

            sector = TimingEvent(
                timestamp=sector_end,
                sector=sector,
                sector_duration=None,
                car=car,
                car_position=-1,
            )

            timing_events.append(sector)

            last_end = sector_end

    timing_events = sorted(timing_events, key=lambda t: t.timestamp)

    # calculate positions and sector durations
    positions_by_sector = {}
    prev_event_by_car: dict[int, TimingEvent] = {}
    for timing_event in timing_events:
        # calculate car position in this sector
        sector = timing_event.sector
        if sector not in positions_by_sector:
            positions_by_sector[sector] = []
        positions_by_sector[sector].append(timing_event.car)
        timing_event.car_position = len(positions_by_sector[sector])

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
