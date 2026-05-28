from dataclasses import dataclass
from datetime import datetime


@dataclass()
class PitEvent:
    """Represents a car entering or exiting the pit lane."""

    timestamp: datetime
    car_number: int
    lap: int
    in_lane: bool
