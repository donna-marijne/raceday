import curses


class CarWidget:
    glyph = "⊵o≗o⌳"

    def __init__(
        self, window: curses.window, color: int, tyre_color: int, in_pit_lane=False
    ):
        self.window = window
        self.color = color
        self.tyre_color = tyre_color
        self.in_pit_lane = in_pit_lane

    def draw(self, y: int, x: int):
        if self.in_pit_lane:
            self.window.addstr(y, x - len(CarWidget.glyph) - 4, "PIT")

        for i, c in enumerate(CarWidget.glyph):
            cur_x = x - len(CarWidget.glyph) + i + 1
            color = self.tyre_color if i == 1 or i == 3 else self.color
            self.window.addch(y, cur_x, c, color)
