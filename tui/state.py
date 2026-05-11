from dataclasses import dataclass


@dataclass()
class CarState:
    number: int
    acronym: str
    color: int
    lap: int
    sector: int
    progress: float


@dataclass()
class RaceState:
    cars: list[CarState]
    total_laps: int
