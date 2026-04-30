from dataclasses import dataclass
from datetime import datetime

from car import Car
from timing_event import TimingEvent


@dataclass
class Session:
    name: str
    start: datetime
    total_laps: int
    cars: dict[int, Car]
    starting_grid: list[Car]
    timing_events: list[TimingEvent]
