from dataclasses import dataclass


@dataclass(frozen=True)
class Sector:
    lap: int
    sector: int

    def next(self) -> "Sector":
        if self.sector == 3:
            return Sector(lap=self.lap + 1, sector=1)
        return Sector(lap=self.lap, sector=self.sector + 1)
