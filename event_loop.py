from datetime import datetime
from time import sleep

from session import Session


def event_loop(
    session: Session, event_callback, time_callback, frequency=60, time_warp=1
):
    interval = 1 / frequency
    queue = list(session.timing_events)
    start_time = queue[0].timestamp
    sim_time = start_time
    wall_time = datetime.now()
    while len(queue) > 0:
        event = queue.pop(0)
        while event.timestamp > sim_time:
            sleep(interval)
            now = datetime.now()
            elapsed_time = now - wall_time
            sim_time += elapsed_time * time_warp
            wall_time = now
            time_callback(sim_time, start_time=start_time)

        event_callback(event)
