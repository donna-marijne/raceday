import curses
from dataclasses import dataclass

import log


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


class RaceView:
    def __init__(self, window: curses.window, lap_scale=3):
        self.window = window
        self.show_laps = lap_scale
        self.y_axis_width = 6
        self.x_axis_height = 2

    def update(self, state: RaceState):
        self.window.erase()

        log.debug(f"state={state}")

        _, window_width = self.window.getmaxyx()
        track_width = window_width - 1 - self.y_axis_width
        sector_width = track_width // (self.show_laps * 3)  # cols per sector
        max_leader_offset = track_width - 2 * sector_width
        leader = state.cars[0]
        leader_col = col_from_progress(
            sector_cols=sector_width,
            lap=leader.lap,
            sector=leader.sector,
            progress=leader.progress,
        )
        leader_offset = min(max_leader_offset, leader_col)
        min_x_col = leader_col - leader_offset

        log.debug(
            f"track_width={track_width} sector_width={sector_width} max_leader_offset={max_leader_offset} leader_col={leader_col} leader_offset={leader_offset} min_x_col={min_x_col}"
        )

        # draw the x axis
        # loop each column and draw for whole laps/sectors
        for x_col in range(min_x_col, min_x_col + track_width):
            progress = x_col % sector_width
            if progress != 0:
                continue

            total_sectors = x_col // sector_width
            lap = (total_sectors // 3) + 1
            sector = (total_sectors % 3) + 1

            x = self.y_axis_width + x_col - min_x_col
            try:
                self.window.move(0, x)
            except:
                raise Exception(
                    f"failed to move to y=1, x={x}; window_width={window_width}"
                )

            if sector == 1:
                # laps start with 1, cars finish after the end
                if lap <= state.total_laps:
                    self.window.addstr(str(lap), curses.A_DIM)
                else:
                    self.window.addstr("🬗🬗🬐")

            else:
                self.window.addch("|", curses.A_DIM)

            if lap > state.total_laps:
                break

        self.window.hline(1, 0, curses.ACS_HLINE, window_width)

        # draw the y axis and cars
        for i, car in enumerate(state.cars):
            y_row = self.x_axis_height + i

            # print the label with 1 col offset
            self.window.addstr(y_row, 1, car.acronym)

            # draw the car
            car_col = col_from_progress(
                sector_cols=sector_width,
                lap=car.lap,
                sector=car.sector,
                progress=car.progress,
            )
            car_x_offset = self.y_axis_width + max(0, car_col - min_x_col)
            self.window.addch(y_row, car_x_offset, " ", curses.A_REVERSE)

        self.window.noutrefresh()


def col_from_progress(sector_cols: int, lap: int, sector: int, progress: float) -> int:
    """Convert lap, sector, and sector progress into a column index"""
    sectors = (((lap - 1) * 3) + (sector - 1)) + progress
    return round(sectors * sector_cols)
