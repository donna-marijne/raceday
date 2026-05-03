import curses

import log


def handle_input(window: curses.window):
    ch = window.getch()
    while ch != -1:
        log.debug(f"handle_input: {ch}")

        if ch == ord("q"):
            exit()

        ch = window.getch()
