from datetime import datetime
from time import sleep

from session import Session


def event_loop(
    session: Session,
    input_callback,
    event_callback,
    time_callback,
    frequency=60,
    time_warp=1,
):
    interval = 1 / frequency
    queue = list(session.timing_events)
    start_time = session.start
    sim_time = start_time
    wall_time = datetime.now()
    while len(queue) > 0:
        # handle user input since the last frame
        input_callback()

        # process the next event
        # sleep if it is in the future (relative to sim_time)
        event = queue.pop(0)
        while event.timestamp > sim_time:
            sleep(interval)

            now = datetime.now()
            elapsed_time = now - wall_time
            sim_time += elapsed_time * time_warp
            wall_time = now
            time_callback(sim_time, start_time=start_time)

        assert event.timestamp <= sim_time
        event_callback(event)
