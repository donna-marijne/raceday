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

    def render_ui(self):
        self._init_colors()

        self.window.move(0, 0)

        # palette sample
        for i in range(0, curses.COLORS):
            self.window.addstr(str(i), curses.color_pair(i))
            self.window.addstr(" ")

        y, _ = self.window.getyx()

        y += 2
        self.window.addstr(
            y,
            3,
            " " + self.session.name + " ",
            curses.A_REVERSE,
        )

        y += 2
        for car in self.session.starting_grid:
            y += 1
            if car is None:
                continue

            color_number = (
                self.color_map[car.color] if car.color in self.color_map else 0
            )
            self.window.addstr(
                y, 1, car.driver_acronym, curses.color_pair(color_number)
            )

        self.msg_y = y

        self.window.refresh()

    def render_timing_event(self, timing_event: TimingEvent):
        str = f"Car {timing_event.car.number} ({timing_event.car.driver_acronym}) completes lap {timing_event.sector.lap} sector {timing_event.sector.sector} in P{timing_event.car_position}"

        self.window.move(self.msg_y, 1)
        self.window.clrtoeol()
        self.window.addstr(str, curses.color_pair(11))
        self.window.refresh()

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
