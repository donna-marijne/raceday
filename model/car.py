from dataclasses import dataclass


@dataclass(frozen=True)
class Car:
    """A car competing in an event."""

    number: int
    driver_name: str
    driver_acronym: str
    team_name: str
    color: str
