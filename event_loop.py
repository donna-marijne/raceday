from datetime import datetime, timedelta
from time import sleep
from typing import Callable

import log
import simulator


def event_loop(
    sim: simulator.Simulator,
    input_callback: Callable[[], None],
    frame_callback: Callable[[simulator.State], None],
    frequency=60,
    time_warp=1,
):
    frame_period = timedelta(seconds=1 / frequency)
    sim_period = frame_period * time_warp
    while True:
        target_next_frame_time = datetime.now() + frame_period

        # check for user input on every frame
        input_callback()

        # simulate a frame multiplied by the warp factor
        sim_start = datetime.now()
        sim.advance(period=sim_period)
        sim_duration = datetime.now() - sim_start

        render_start = datetime.now()
        frame_callback(sim.state)
        render_duration = datetime.now() - render_start

        log.debug(
            f"event_loop: sim_duration={sim_duration} render_duration={render_duration}"
        )

        # sleep to the target
        sleep_seconds = (target_next_frame_time - datetime.now()).total_seconds()
        # assert sleep_seconds > 0, f"sleep_seconds={sleep_seconds}"
        if sleep_seconds > 0:
            sleep(sleep_seconds)
