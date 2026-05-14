from dataclasses import dataclass

from model.tyre_compound import TyreCompound


@dataclass()
class Stint:
    number: int
    car_number: int
    lap_start: int
    tyre_compound: TyreCompound
    tyre_age_at_start: int
