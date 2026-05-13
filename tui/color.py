import curses
from typing import Tuple

# map hex color -> curses color
_color_map: dict[str, int] = {}

FIRST_CUSTOM_COLOR_NUMBER = 16


def init_colors(hex_colors: list[str]):
    """Set up the default and provided hex colors in curses"""
    if not curses.has_colors():
        return

    # enable color with default palette
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1)

    # add custom colors if supported
    if not curses.can_change_color():
        return

    next_color_number = FIRST_CUSTOM_COLOR_NUMBER
    for hex_color in hex_colors:
        if hex_color in _color_map:
            continue

        r, g, b = _curses_color_from_hex_string(hex_color)
        curses.init_color(next_color_number, r, g, b)
        curses.init_pair(next_color_number, next_color_number, -1)
        _color_map[hex_color] = next_color_number
        next_color_number += 1


def color_pair_from_hex(hex_color: str) -> int:
    """Get the curses color pair number for the provided hex color, or 0 if the color was not initialized"""
    color_number = _color_map[hex_color] if hex_color in _color_map else 0
    return curses.color_pair(color_number)


def _curses_color_from_hex_string(hex_string) -> Tuple[int, int, int]:
    """Convert a hex string to curses-compatible RGB 0-999 tuple"""
    scale = 1000 / 255
    r, g, b = int(hex_string[:2], 16), int(hex_string[2:4], 16), int(hex_string[4:], 16)

    return int(r * scale), int(g * scale), int(b * scale)
