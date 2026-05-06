from session import Session
from tui.race_view import CarState, RaceState


def race_state_from_session(session: Session, color_map: dict[str, int]) -> RaceState:
    car_states = []
    for car in session.starting_grid:
        car_state = CarState(
            number=car.number,
            acronym=car.driver_acronym,
            color=color_map[car.color],
            lap=1,
            sector=1,
            progress=0,
        )
        car_states.append(car_state)

    race_state = RaceState(cars=car_states, total_laps=session.total_laps)

    return race_state
