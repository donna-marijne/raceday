import curses


class Car:
    glyph = "⊵o≗o⌳"

    def __init__(self, window: curses.window, color: int, tyre_color: int):
        self.window = window
        self.color = color
        self.tyre_color = tyre_color

    def draw(self, y: int, x: int):
        for i, c in enumerate(Car.glyph):
            cur_x = x - len(Car.glyph) + i + 1
            color = self.tyre_color if i == 1 or i == 3 else self.color
            self.window.addch(y, cur_x, c, curses.color_pair(color))
