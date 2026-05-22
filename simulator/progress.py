from dataclasses import dataclass


@dataclass
class Progress:
    lap: int
    sector: int
    fraction: float

    def __gt__(self, other):
        if self.lap > other.lap:
            return True

        if self.lap == other.lap:
            if self.sector > other.sector:
                return True

            if self.sector == other.sector:
                return self.fraction > other.fraction

        return False
