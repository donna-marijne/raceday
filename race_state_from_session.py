from session import Session
from tui.race_view import CarState, RaceState


def race_state_from_session(session: Session, color_map: dict[str, int]) -> RaceState:
    car_states = []
    for car in session.starting_grid:
        first_sector_duration = None
        if car.number in session.timing_events_by_car:
            timing_events = session.timing_events_by_car[car.number]
            if len(timing_events) > 0:
                first_sector_duration = timing_events[0].timestamp - session.start

        car_state = CarState(
            number=car.number,
            acronym=car.driver_acronym,
            color=color_map[car.color],
            lap=1,
            sector=1,
            progress=0,
            sector_start=session.start,
            sector_duration=first_sector_duration,
        )
        car_states.append(car_state)

    race_state = RaceState(cars=car_states, total_laps=session.total_laps)

    return race_state
