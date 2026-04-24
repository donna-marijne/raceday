from dataclasses import dataclass


@dataclass(frozen=True)
class Car:
    """A car competing in an event."""

    number: int
