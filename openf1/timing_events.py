import json
from datetime import datetime, timedelta
from os import path

from car import Car
from sector import Sector
from timing_event import TimingEvent


def timing_events_from_source_dir(dir_path):
    laps_file_path = path.join(dir_path, "laps.json")

    laps_json_str = None
    with open(laps_file_path, "r") as laps_file:
        laps_json_str = laps_file.read()

    return timing_events_from_json(laps_json_str)


def timing_events_from_json(laps_json_str):
    """Returns a list of TimingEvents ordered by timestamp"""

    laps = json.loads(laps_json_str)

    timing_events = []
    cars = {}
    positions_by_sector = {}
    for lap in laps:
        date_start = lap["date_start"]
        duration_sector_1 = lap["duration_sector_1"]
        duration_sector_2 = lap["duration_sector_2"]
        duration_sector_3 = lap["duration_sector_3"]
        driver_number = lap["driver_number"]
        lap_number = lap["lap_number"]

        if driver_number not in cars:
            cars[driver_number] = Car(number=driver_number)
        car = cars[driver_number]

        last_end = datetime.fromisoformat(date_start)
        for i, duration in enumerate(
            [duration_sector_1, duration_sector_2, duration_sector_3]
        ):
            if duration == None:
                continue

            sector_end = last_end + timedelta(seconds=duration)

            sector = Sector(lap_number, i + 1)

            if sector not in positions_by_sector:
                positions_by_sector[sector] = []
            positions_by_sector[sector].append(car)
            car_position = len(positions_by_sector[sector])

            sector = TimingEvent(
                timestamp=sector_end,
                sector=sector,
                car=car,
                car_position=car_position,
            )

            timing_events.append(sector)

            last_end = sector_end

    return sorted(timing_events, key=lambda t: t.timestamp)
