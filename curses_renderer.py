import curses


class CursesRenderer:
    def __init__(self, window):
        self.window = window

        # enable color with default palette
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i, i, -1)

        # hide the cursor
        curses.curs_set(0)

    def render_ui(self):
        self.window.move(0, 0)

        # palette sample
        for i in range(0, curses.COLORS):
            self.window.addstr(str(i), curses.color_pair(i))
            self.window.addstr(" ")

        y, _ = self.window.getyx()

        self.window.addstr(
            y + 2,
            3,
            " Heinz Baked Beans Grand Prix of Northern Ireland ",
            curses.A_REVERSE,
        )
        self.window.addstr(y + 4, 1, "HAM", curses.color_pair(9))
        self.msg_y = y + 6
        self.window.refresh()

    def render_timing_event(self, timing_event):
        str = f"Car {timing_event.car.number} completes lap {timing_event.sector.lap} sector {timing_event.sector.sector} in P{timing_event.car_position}"

        self.window.move(self.msg_y, 1)
        self.window.clrtoeol()
        self.window.addstr(str, curses.color_pair(11))
        self.window.refresh()
