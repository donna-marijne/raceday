from dataclasses import dataclass
from datetime import datetime

from .car import Car
from .car_state import CarState
from .timing_event import TimingEvent


@dataclass
class Session:
    name: str
    start: datetime
    total_laps: int
    cars: dict[int, Car]
    starting_grid: list[CarState]
    timing_events: list[TimingEvent]
    timing_events_by_car: dict[int, list[TimingEvent]]
