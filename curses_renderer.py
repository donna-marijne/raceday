import curses
from datetime import datetime

import log
from car import Car
from curses_color import curses_color_from_hex_string
from format_timedelta import format_timedelta
from race_state_from_session import race_state_from_session
from session import Session
from timing_event import TimingEvent
from tui.race_view import RaceView
from tyre_colors import TYRE_COLORS
from tyre_compound import TyreCompound


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

        # set non-blocking input mode
        self.window.nodelay(True)

        self._init_colors()

        self.race_state = race_state_from_session(session, color_map=self.color_map)

    def render_ui(self):
        _, window_width = self.window.getmaxyx()

        self.window.move(0, 0)

        # palette sample
        for i in range(0, curses.COLORS):
            self.window.addstr(str(i), curses.color_pair(i))
            self.window.addstr(" ")

        # session name
        self.header_y, _ = self._move(dy=2, x=3)
        self.window.addstr(" " + self.session.name + " ", curses.A_REVERSE)
        self.window.addstr(
            " " + self.session.start.strftime("%-d %B") + " ",
            curses.color_pair(3) | curses.A_REVERSE,
        )

        # race view component
        race_view_window = self.window.subwin(
            len(self.session.starting_grid) + 2,
            window_width,
            self.header_y + 2,
            0,
        )
        self.race_view = RaceView(window=race_view_window)
        self.race_view.update(self.race_state)

        self.window.refresh()

    def render_timing_event(self, timing_event: TimingEvent):
        log.debug(f"render_timing_event: {timing_event}")

        car_states = self.race_state.cars
        car = timing_event.car
        car_index = timing_event.car_state.position - 1

        if car_states[car_index].number != car.number:
            old_car_index = None
            for i, cs in enumerate(car_states):
                if cs.number == car.number:
                    old_car_index = i
                    break
            assert old_car_index is not None
            car_state = car_states.pop(old_car_index)
            car_states.insert(car_index, car_state)

        car_state = car_states[car_index]
        completed_sector = timing_event.sector
        if completed_sector.sector == 3:
            car_state.lap = completed_sector.lap + 1
            car_state.sector = 1
        else:
            car_state.lap = completed_sector.lap
            car_state.sector = completed_sector.sector + 1
        car_state.progress = 0.0
        car_state.sector_start = timing_event.timestamp
        car_state.sector_duration = timing_event.sector_duration

        self.race_view.update(self.race_state)

        curses.doupdate()

    def render_clock(self, timestamp: datetime, start_time: datetime):
        race_time = timestamp - start_time
        str = f" {format_timedelta(race_time)} "
        _, max_x = self.window.getmaxyx()
        x = max_x - len(str) - 1
        self._move(self.header_y, x)
        self.window.addstr(str, curses.A_REVERSE)

        self._update_car_states(timestamp)
        self.race_view.update(self.race_state)

        self.window.noutrefresh()

        curses.doupdate()

    def _update_car_states(self, timestamp: datetime):
        for car_state in self.race_state.cars:
            if car_state.sector_duration is None:
                continue

            since_sector_start = timestamp - car_state.sector_start
            car_state.progress = since_sector_start / car_state.sector_duration

    def _color_pair_for_car(self, car: Car) -> int:
        color_number = self.color_map[car.color] if car.color in self.color_map else 0
        return curses.color_pair(color_number)

    def _color_pair_for_tyre_compound(self, tyre_compound: TyreCompound) -> int:
        hex_color = TYRE_COLORS[tyre_compound]
        color_number = self.color_map[hex_color] if hex_color in self.color_map else 0
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

        try:
            self.window.move(next_y, next_x)
        except:
            raise ValueError(f"failed to move to y={next_y}, x={next_x}")

        return next_y, next_x

    def _init_colors(self):
        if not curses.can_change_color():
            return

        self.color_map = {}
        next_color_number = 16
        tyres: list[str] = [TYRE_COLORS[e.value] for e in TyreCompound]
        car_colors = [car.color for car in self.session.cars.values()]
        for hex_color in tyres + car_colors:
            if hex_color in self.color_map:
                continue

            r, g, b = curses_color_from_hex_string(hex_color)
            curses.init_color(next_color_number, r, g, b)
            curses.init_pair(next_color_number, next_color_number, -1)
            self.color_map[hex_color] = next_color_number
            next_color_number += 1
