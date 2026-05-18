import model
from tyre_colors import TYRE_COLORS

from .color import color_pair_from_hex
from .race_view import CarState, RaceState


def race_state_from_session(session: model.Session) -> RaceState:
    car_states = []
    for grid_slot in session.starting_grid:
        car_number = grid_slot.number
        first_sector_duration = None
        if car_number in session.timing_events_by_car:
            timing_events = session.timing_events_by_car[car_number]
            if len(timing_events) > 0:
                first_sector_duration = timing_events[0].timestamp - session.start

        car = session.cars[car_number]

        car_state = CarState(
            number=car.number,
            acronym=car.driver_acronym,
            color=color_pair_from_hex(car.color),
            tyre_color=color_pair_from_hex(TYRE_COLORS[grid_slot.tyre_compound]),
            tyre_age=grid_slot.tyre_age,
            lap=1,
            sector=1,
            progress=0,
            sector_start=session.start,
            sector_duration=first_sector_duration,
        )
        car_states.append(car_state)

    race_state = RaceState(cars=car_states, total_laps=session.total_laps)

    return race_state
