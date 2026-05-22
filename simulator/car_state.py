from dataclasses import dataclass
from typing import Optional

import model

from .progress import Progress


@dataclass()
class CarState:
    car: model.Car
    previous_timing_event: Optional[model.TimingEvent]
    next_timing_event: Optional[model.TimingEvent]
    tyre_compound: model.TyreCompound
    tyre_age: int
    progress: Progress
    in_pit_lane: bool
