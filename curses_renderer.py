import curses

from curses_color import curses_color_from_hex_string
from session import Session
from timing_event import TimingEvent


class CursesRenderer:
    def __init__(self, window: curses.window, session: Session):
        self.window = window
        self.session = session

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

        # x axis (lap numbers)
        self.lap_offset_x = 6
        self._move(dy=2, x=self.lap_offset_x)
        for i in range(0, self.session.total_laps):
            self.window.addstr(str(i + 1).ljust(3, " "), curses.A_DIM)

        self._move(dy=1, x=self.lap_offset_x)
        self.window.hline(curses.ACS_HLINE, self.session.total_laps * 3)

        # y axis (car labels)
        self.first_driver_label_yx = self._move(dy=1, x=1)
        self.first_car_origin = self.first_driver_label_yx[0], self.lap_offset_x
        for car in self.session.starting_grid:
            if car is None:
                continue

            color_number = (
                self.color_map[car.color] if car.color in self.color_map else 0
            )
            self.window.addstr(car.driver_acronym, curses.color_pair(color_number))
            self._move(dy=1, x=1)

        self.msg_yx = self._move(dy=1, x=1)

        self.window.refresh()

    def render_timing_event(self, timing_event: TimingEvent):
        str = f"Car {timing_event.car.number} ({timing_event.car.driver_acronym}) completes lap {timing_event.sector.lap} sector {timing_event.sector.sector} in P{timing_event.car_position}"

        self.window.move(*self.msg_yx)
        self.window.clrtoeol()
        self.window.addstr(str, curses.color_pair(11))
        self.window.refresh()

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
