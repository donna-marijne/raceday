import json
from dataclasses import dataclass
from typing import TypeAlias

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


@dataclass
class OpenF1Payload:
    session: dict[str, JSON]
    meeting: dict[str, JSON]
    drivers: list[dict[str, JSON]]
    starting_grid: list[dict[str, JSON]]
    laps: list[dict[str, JSON]]

    @classmethod
    def from_source_dir(cls, dir_path):
        session = None
        with (dir_path / "sessions.json").open("r") as sessions_file:
            json_str = sessions_file.read()
            sessions = json.loads(json_str)
            if len(sessions) != 1:
                raise ValueError(f"unexpectedly saw {len(sessions)} sessions")
            session = sessions[0]

        meeting = None
        with (dir_path / "meetings.json").open("r") as meetings_file:
            json_str = meetings_file.read()
            meetings = json.loads(json_str)
            if len(meetings) != 1:
                raise ValueError(f"unexpectedly saw {len(meetings)} meetings")
            meeting = meetings[0]

        drivers = None
        with (dir_path / "drivers.json").open("r") as drivers_file:
            json_str = drivers_file.read()
            drivers = json.loads(json_str)

        starting_grid = None
        with (dir_path / "starting_grid.json").open("r") as starting_grid_file:
            json_str = starting_grid_file.read()
            starting_grid = json.loads(json_str)

        laps = None
        with (dir_path / "laps.json").open("r") as laps_file:
            json_str = laps_file.read()
            laps = json.loads(json_str)

        return cls(
            session=session,
            meeting=meeting,
            drivers=drivers,
            starting_grid=starting_grid,
            laps=laps,
        )
