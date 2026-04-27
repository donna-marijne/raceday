from datetime import datetime, timedelta

from sector import Sector
from timing_event import TimingEvent


def timing_events_from_api_laps(laps, cars):
    """Returns a list of TimingEvents ordered by timestamp"""

    timing_events = []
    for lap in laps:
        date_start = lap["date_start"]
        duration_sector_1 = lap["duration_sector_1"]
        duration_sector_2 = lap["duration_sector_2"]
        duration_sector_3 = lap["duration_sector_3"]
        driver_number = lap["driver_number"]
        lap_number = lap["lap_number"]

        car = cars[driver_number]

        if date_start is None:
            # DNS(?)
            continue

        last_end = datetime.fromisoformat(date_start)
        for i, duration in enumerate(
            [duration_sector_1, duration_sector_2, duration_sector_3]
        ):
            if duration == None:
                continue

            sector_end = last_end + timedelta(seconds=duration)

            sector = Sector(lap_number, i + 1)

            sector = TimingEvent(
                timestamp=sector_end,
                sector=sector,
                car=car,
                car_position=-1,
            )

            timing_events.append(sector)

            last_end = sector_end

    timing_events = sorted(timing_events, key=lambda t: t.timestamp)

    positions_by_sector = {}
    for timing_event in timing_events:
        sector = timing_event.sector
        if sector not in positions_by_sector:
            positions_by_sector[sector] = []
        positions_by_sector[sector].append(timing_event.car)
        timing_event.car_position = len(positions_by_sector[sector])

    return timing_events
