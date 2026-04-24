from dataclasses import dataclass


@dataclass(frozen=True)
class Sector:
    lap: int
    sector: int
