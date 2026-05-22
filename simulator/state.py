from dataclasses import dataclass
from datetime import datetime

import model

from .car_state import CarState


@dataclass()
class State:
    session: model.Session
    timestamp: datetime
    cars: list[CarState]
