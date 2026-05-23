from dataclasses import dataclass

from .tyre_compound import TyreCompound


# TODO: remove
@dataclass()
class CarState:
    """Represents the state of a car at a single point in time"""

    number: int
    tyre_age: int
    tyre_compound: TyreCompound
