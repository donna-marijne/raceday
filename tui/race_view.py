import curses
from typing import Tuple

import simulator
from tui.color import color_pair_from_hex
from tyre_colors import TYRE_COLORS

from .car_widget import CarWidget


class RaceView:
    def __init__(
        self,
        window: curses.window,
        state: simulator.State,
        lap_scale: int,
        sector_split: Tuple[float, float, float],
    ):
        self.window = window
        self.state = state
        self.show_laps = lap_scale
        self.sector_split = sector_split
        self.y_axis_width = 9 + len(CarWidget.glyph)
        self.x_axis_height = 2
        self.car_widgets: dict[int, CarWidget] = {}

    def first_render(self):
        self.update()

    def update(self):
        self.window.erase()

        _, window_width = self.window.getmaxyx()
        track_width = window_width - 1 - self.y_axis_width
        lap_width = track_width // self.show_laps
        sector_1_cols = round(float(lap_width) * self.sector_split[0])
        sector_2_cols = round(float(lap_width) * self.sector_split[1])
        sector_3_cols = lap_width - (
            sector_1_cols + sector_2_cols
        )  # to avoid rounding issues
        max_leader_offset = track_width - (lap_width // 2)
        leader = self.state.cars[0]
        leader_col = col_from_progress(
            lap_cols=lap_width,
            sector_cols=(sector_1_cols, sector_2_cols, sector_3_cols),
            lap=leader.progress.lap,
            sector=leader.progress.sector,
            progress=leader.progress.fraction,
        )
        leader_offset = min(max_leader_offset, leader_col)
        min_x_col = leader_col - leader_offset

        # log.debug(
        #     f"track_width={track_width} lap_width={lap_width} sector_cols={sector_1_cols},{sector_2_cols},{sector_3_cols} max_leader_offset={max_leader_offset} leader_col={leader_col} leader_offset={leader_offset} min_x_col={min_x_col}"
        # )

        # draw the x axis
        x_axis_labels_y = 0
        x_axis_y = 1

        self.window.attron(curses.A_DIM)

        self.window.addstr(x_axis_y, 0, "━" * self.y_axis_width)

        sector_1_offset = sector_1_cols
        sector_2_offset = sector_1_cols + sector_2_cols

        # loop each column and draw for whole laps/sectors
        for x_col in range(min_x_col, min_x_col + track_width):
            lap_progress = x_col % lap_width

            lap = (x_col // lap_width) + 1
            progress = lap_progress
            if lap_progress >= sector_2_offset:
                progress = lap_progress - sector_2_offset
            elif lap_progress >= sector_1_offset:
                progress = lap_progress - sector_1_offset

            x = self.y_axis_width + x_col - min_x_col

            # labels row
            self.window.move(x_axis_labels_y, x)

            if lap_progress == 0:
                # laps start with 1, cars finish after the end
                if lap <= self.state.session.total_laps:
                    self.window.addstr(str(lap))
                else:
                    self.window.addstr("🬗🬗🬐", curses.A_NORMAL)

            # axis row
            self.window.move(x_axis_y, x)
            if progress == 0:
                self.window.addch("┷")
            else:
                self.window.addch("━")

            if lap > self.state.session.total_laps:
                break

        self.window.attroff(curses.A_DIM)

        # draw the y axis and cars
        for i, car_state in enumerate(self.state.cars):
            y_row = self.x_axis_height + i

            car = car_state.car
            car_color = color_pair_from_hex(car.color)
            tyre_color = color_pair_from_hex(TYRE_COLORS[car_state.tyre_compound])

            # print the label with 1 col offset
            self.window.addstr(y_row, 1, car_state.car.driver_acronym, car_color)

            # print the tyre age
            self.window.addstr(y_row, 5, f"{car_state.tyre_age:>2}", tyre_color)

            # draw the car
            progress = car_state.progress
            car_col = col_from_progress(
                lap_cols=lap_width,
                sector_cols=(sector_1_cols, sector_2_cols, sector_3_cols),
                lap=progress.lap,
                sector=progress.sector,
                progress=progress.fraction,
            )
            car_x_offset = self.y_axis_width + max(0, car_col - min_x_col)
            self._draw_car(car_state, y=y_row, x=car_x_offset)

        self.window.noutrefresh()

    def _draw_car(self, car_state: simulator.CarState, y: int, x: int):
        car = car_state.car
        tyre_color = color_pair_from_hex(TYRE_COLORS[car_state.tyre_compound])

        if car.number not in self.car_widgets:
            car_color = color_pair_from_hex(car.color)
            self.car_widgets[car.number] = CarWidget(
                window=self.window,
                color=car_color,
                tyre_color=tyre_color,
            )

        self.car_widgets[car.number].tyre_color = tyre_color
        self.car_widgets[car.number].draw(y=y, x=x)


def col_from_progress(
    lap_cols: int,
    sector_cols: Tuple[int, int, int],
    lap: int,
    sector: int,
    progress: float,
) -> int:
    """Convert lap, sector, and sector progress into a column index"""
    col = (lap - 1) * lap_cols
    for i in range(0, sector - 1):
        col += sector_cols[i]
    col += round(sector_cols[sector - 1] * progress)

    return col
