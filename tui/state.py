from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass()
class CarState:
    number: int
    acronym: str
    color: int
    tyre_color: int
    tyre_age: int
    lap: int
    sector: int
    progress: float
    sector_start: datetime
    sector_duration: Optional[timedelta]


@dataclass()
class RaceState:
    cars: list[CarState]
    total_laps: int
