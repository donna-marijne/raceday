import curses

from car import Car
from curses_color import curses_color_from_hex_string
from sector import Sector
from session import Session
from timing_event import TimingEvent


class CursesRenderer:
    def __init__(self, window: curses.window, session: Session):
        self.window = window
        self.session = session
        self.current_row_by_car = {}

        # enable color with default palette
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i, i, -1)

        # hide the cursor
        curses.curs_set(0)

        self._init_colors()

    def render_ui(self):
        self.window.move(0, 0)

        # palette sample
        for i in range(0, curses.COLORS):
            self.window.addstr(str(i), curses.color_pair(i))
            self.window.addstr(" ")

        # session name
        self._move(dy=2, x=3)
        self.window.addstr(" " + self.session.name + " ", curses.A_REVERSE)
        self.window.addstr(
            " " + self.session.start.strftime("%-d %B") + " ",
            curses.color_pair(3) | curses.A_REVERSE,
        )

        # x axis (lap numbers)
        self.lap_offset_x = 6
        self._move(dy=2, x=self.lap_offset_x)
        for i in range(0, self.session.total_laps):
            self.window.addstr(str(i + 1).ljust(3, " "), curses.A_DIM)

        self._move(dy=1, x=self.lap_offset_x)
        self.window.hline(curses.ACS_HLINE, self.session.total_laps * 3)

        # y axis (car labels)
        first_car_y, _ = self._move(dy=1, x=1)
        self.first_car_row_y = first_car_y
        for row, car in enumerate(self.session.starting_grid):
            if car is None:
                continue

            self.current_row_by_car[car.number] = row

            self._insert_car_row(first_car_y + 0, car)

        self.window.refresh()

    def render_timing_event(self, timing_event: TimingEvent):
        car = timing_event.car

        # delete the old row with the car
        assert car.number in self.current_row_by_car
        old_row = self.current_row_by_car[car.number]
        old_y = self.first_car_row_y + old_row
        self._move(y=old_y, x=0)
        self.window.deleteln()
        for car_number, row in self.current_row_by_car.items():
            if row > old_row:
                self.current_row_by_car[car_number] -= 1

        new_row = timing_event.car_position - 1
        new_y = self.first_car_row_y + new_row
        self._insert_car_row(new_y, car, timing_event.sector)
        for car_number, row in self.current_row_by_car.items():
            if row >= new_row:
                self.current_row_by_car[car_number] += 1
        self.current_row_by_car[car.number] = new_row

        self.window.refresh()

    def _insert_car_row(self, y: int, car: Car, sector: Sector | None = None):
        self._move(y=y, x=0)
        self.window.insertln()

        self._move(y=y, x=1)
        self.window.addstr(car.driver_acronym, self._color_pair_for_car(car))

        x = ((sector.lap - 1) * 3 + sector.sector) if sector else 0
        self._move(x=self.lap_offset_x + x)
        self._render_car(car)

    def _color_pair_for_car(self, car: Car) -> int:
        color_number = self.color_map[car.color] if car.color in self.color_map else 0
        return curses.color_pair(color_number)

    def _render_car(self, car: Car):
        self.window.addch(" ", self._color_pair_for_car(car) | curses.A_REVERSE)

    def _move(self, y=None, x=None, dy=None, dx=None):
        next_y, next_x = self.window.getyx()
        if y is not None:
            next_y = y
        if x is not None:
            next_x = x
        if dy is not None:
            next_y += dy
        if dx is not None:
            next_x += dx

        self.window.move(next_y, next_x)

        return next_y, next_x

    def _init_colors(self):
        if not curses.can_change_color():
            return

        self.color_map = {}
        next_color_number = 16
        for car in self.session.cars.values():
            hex_color = car.color
            if hex_color in self.color_map:
                continue

            r, g, b = curses_color_from_hex_string(hex_color)
            curses.init_color(next_color_number, r, g, b)
            curses.init_pair(next_color_number, next_color_number, -1)
            self.color_map[hex_color] = next_color_number
            next_color_number += 1
