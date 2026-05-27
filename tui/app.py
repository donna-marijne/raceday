import curses

import simulator
from tyre_colors import TYRE_COLORS

from .color import init_colors
from .header_view import HeaderView
from .race_view import RaceView


class App:
    def __init__(self, window: curses.window, state: simulator.State):
        self.window = window
        self.state = state

        self._init_colors()

        # hide the cursor
        curses.curs_set(0)

        # set non-blocking input mode
        self.window.nodelay(True)

    def first_render(self):
        _, max_x = self.window.getmaxyx()

        header_window = self.window.subwin(1, max_x, 0, 0)
        self.header_view = HeaderView(
            window=header_window,
            session_name=self.state.session.name,
            session_start=self.state.session.start,
        )
        self.header_view.first_render()

        race_view_window = self.window.subwin(
            len(self.state.cars) + 2,
            max_x,
            2,
            0,
        )
        self.race_view = RaceView(
            window=race_view_window,
            state=self.state,
            lap_scale=3,
            sector_split=self.state.session.sector_split,
        )
        self.race_view.first_render()

        curses.doupdate()

    def update(self, state: simulator.State):
        self.header_view.sim_time = state.timestamp
        self.header_view.update()

        self.race_view.state = state
        self.race_view.update()

        curses.doupdate()

    def _init_colors(self):
        tyre_colors = list(TYRE_COLORS.values())
        car_colors = [car_state.car.color for car_state in self.state.cars]
        init_colors(tyre_colors + car_colors)
