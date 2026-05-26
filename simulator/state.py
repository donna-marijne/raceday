from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import model

from .car_state import CarState


@dataclass()
class State:
    session: model.Session
    timestamp: datetime
    previous_timestamp: Optional[datetime]
    cars: list[CarState]
