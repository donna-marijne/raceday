import curses
from datetime import datetime
from typing import Optional

import log
import model
from tyre_colors import TYRE_COLORS

from .color import init_colors
from .header import Header
from .race_state_from_session import race_state_from_session
from .race_view import RaceView


class App:
    def __init__(self, window: curses.window, session: model.Session):
        self.window = window
        self.session = session

        self._init_colors()

        # hide the cursor
        curses.curs_set(0)

        # set non-blocking input mode
        self.window.nodelay(True)

        self.race_state = race_state_from_session(session)

    def first_render(self):
        _, max_x = self.window.getmaxyx()

        header_window = self.window.subwin(1, max_x, 0, 0)
        self.header = Header(
            window=header_window,
            session_name=self.session.name,
            session_start=self.session.start,
        )
        self.header.first_render()

        race_view_window = self.window.subwin(
            len(self.session.starting_grid) + 2,
            max_x,
            2,
            0,
        )
        self.race_view = RaceView(window=race_view_window)
        self.race_view.update(self.race_state)

        curses.doupdate()

    def update(
        self,
        timestamp: datetime,
        timing_event: Optional[model.TimingEvent] = None,
    ):
        if timing_event is not None:
            self._render_timing_event(timing_event)

        self._render_tick(timestamp)

        curses.doupdate()

    def _init_colors(self):
        tyre_colors = list(TYRE_COLORS.values())
        car_colors = [car.color for car in self.session.cars.values()]
        init_colors(tyre_colors + car_colors)

    def _render_timing_event(self, timing_event: model.TimingEvent):
        log.debug(f"_render_timing_event: {timing_event}")

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

    def _render_tick(self, timestamp: datetime):
        log.debug(f"_render_tick: {timestamp}")

        self.header.sim_time = timestamp
        self.header.update()

        self._update_car_states(timestamp)
        self.race_view.update(self.race_state)

    def _update_car_states(self, timestamp: datetime):
        for car_state in self.race_state.cars:
            if car_state.sector_duration is None:
                continue

            since_sector_start = timestamp - car_state.sector_start
            car_state.progress = since_sector_start / car_state.sector_duration
