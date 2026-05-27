from dataclasses import dataclass
from datetime import datetime

from model.car import Car


@dataclass()
class PitEvent:
    """Represents a car entering or exiting the pit lane."""

    timestamp: datetime
    car: Car
    in_lane: bool
