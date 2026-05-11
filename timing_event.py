from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from car import Car
from sector import Sector


@dataclass
class TimingEvent:
    """Represents the time that a car completes a sector in a race."""

    timestamp: datetime
    sector: Sector
    sector_duration: Optional[timedelta]
    car: Car
    car_position: int
