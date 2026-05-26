from datetime import timedelta

import log
import model
from openf1 import json_validation
from openf1.openf1_payload import OpenF1Payload


def timing_events_from_api(
    payload: OpenF1Payload,
    cars: dict[int, model.Car],
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

            sector = model.TimingEvent(
                timestamp=sector_end,
                sector=sector,
                car=car,
            )

            timing_events.append(sector)

            last_end = sector_end

    timing_events = sorted(timing_events, key=lambda t: t.timestamp)

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
