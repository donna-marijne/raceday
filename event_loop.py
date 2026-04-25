from datetime import datetime
from time import sleep


def event_loop(timing_events, callback, frequency=60, time_warp=1):
    interval = 1 / frequency
    queue = list(timing_events)
    sim_time = queue[0].timestamp
    wall_time = datetime.now()
    while len(queue) > 0:
        event = queue.pop(0)
        while event.timestamp > sim_time:
            sleep(interval)
            now = datetime.now()
            elapsed_time = now - wall_time
            sim_time += elapsed_time * time_warp
            wall_time = now

        callback(event)
