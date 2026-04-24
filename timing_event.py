from dataclasses import dataclass
from datetime import datetime

from car import Car
from sector import Sector


@dataclass(frozen=True)
class TimingEvent:
    """Represents the time that a car completes a sector in a race."""

    timestamp: datetime
    sector: Sector
    car: Car
    car_position: int
