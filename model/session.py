from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from .car import Car
from .pit_event import PitEvent
from .stint import Stint
from .timing_event import TimingEvent


@dataclass
class Session:
    name: str
    start: datetime
    sector_split: Tuple[float, float, float]
    total_laps: int
    cars: dict[int, Car]
    starting_grid: list[int]
    stints: dict[int, list[Stint]]
    pit_events_by_car: dict[int, list[PitEvent]]
    timing_events: list[TimingEvent]
    timing_events_by_car: dict[int, list[TimingEvent]]
