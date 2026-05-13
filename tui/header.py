import curses
from datetime import datetime
from typing import Optional

from format_timedelta import format_timedelta


class Header:
    def __init__(
        self,
        window: curses.window,
        session_name: str,
        session_start: datetime,
        sim_time: Optional[datetime] = None,
    ):
        self.window = window
        self.session_name = session_name
        self.session_start = session_start
        self.sim_time = sim_time

    def first_render(self):
        self.window.move(0, 0)
        self.window.addstr(" " + self.session_name + " ", curses.A_REVERSE)
        self.window.addstr(
            " " + self.session_start.strftime("%-d %B") + " ",
            curses.color_pair(curses.COLOR_YELLOW) | curses.A_REVERSE,
        )

        self.window.noutrefresh()

    def update(self):
        if self.sim_time is None:
            return

        race_time = self.sim_time - self.session_start
        str = f" {format_timedelta(race_time)} "
        _, max_x = self.window.getmaxyx()
        x = max_x - len(str) - 1
        self.window.move(0, x)
        self.window.addstr(str, curses.A_REVERSE)

        self.window.noutrefresh()
