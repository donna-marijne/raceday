def curses_color_from_hex_string(hex_string):
    scale = 1000 / 255
    r, g, b = int(hex_string[:2], 16), int(hex_string[2:4], 16), int(hex_string[4:], 16)
    return int(r * scale), int(g * scale), int(b * scale)
