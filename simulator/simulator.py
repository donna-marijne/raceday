from datetime import timedelta
from typing import Optional, Tuple

import model

from .car_state import CarState
from .progress import Progress
from .state import State


class Simulator:
    def __init__(self, session: model.Session):
        self.session = session
        self.state = self._init_state()
        self.timing_event_index_by_car: dict[int, int] = {}
        for car in self.session.starting_grid:
            self.timing_event_index_by_car[car.number] = 0

    def advance(self, period: timedelta):
        self.state.previous_timestamp = self.state.timestamp
        self.state.timestamp += period

        for car_state in self.state.cars:
            assert car_state.previous_timing_event is not None
            if car_state.next_timing_event is None:
                # car has retired, nothing more to do
                continue

            car_number = car_state.car.number
            previous_timing_event, next_timing_event = (
                self._find_previous_and_next_timing_events(car_number)
            )
            if previous_timing_event is not None:
                car_state.previous_timing_event = previous_timing_event
            car_state.next_timing_event = next_timing_event

            self._update_car_progress(car_state=car_state)

            stint = self._find_current_stint(car_state=car_state)
            car_state.tyre_compound = stint.tyre_compound
            car_state.tyre_age = stint.tyre_age_at_start + (
                car_state.progress.lap - stint.lap_start
            )

        self.state.cars.sort(key=lambda car_state: car_state.progress, reverse=True)

    def _init_state(self) -> State:
        car_states: list[CarState] = []
        for car_starting_state in self.session.starting_grid:
            car_number = car_starting_state.number
            car = self.session.cars[car_number]
            stint = self.session.stints[car_number][0]

            # fake timing event for race start
            previous_timing_event = model.TimingEvent(
                timestamp=self.session.start,
                sector=model.Sector(lap=1, sector=1),
                car=car,
            )

            next_timing_event: Optional[model.TimingEvent] = None
            if car_number in self.session.timing_events_by_car:
                timing_events = self.session.timing_events_by_car[car_number]
                if len(timing_events) > 0:
                    next_timing_event = timing_events[0]

            car_state = CarState(
                car=car,
                previous_timing_event=previous_timing_event,
                next_timing_event=next_timing_event,
                tyre_compound=stint.tyre_compound,
                tyre_age=stint.tyre_age_at_start,
                progress=Progress(lap=1, sector=1, fraction=0.0),
                in_pit_lane=False,
            )
            car_states.append(car_state)

        state = State(
            session=self.session,
            timestamp=self.session.start,
            previous_timestamp=None,
            cars=car_states,
        )

        return state

    def _find_previous_and_next_timing_events(
        self, car: int
    ) -> Tuple[Optional[model.TimingEvent], Optional[model.TimingEvent]]:
        from_index = self.timing_event_index_by_car[car]
        timing_events = self.session.timing_events_by_car[car][from_index:]

        previous_timing_event = None
        for i, timing_event in enumerate(timing_events):
            if timing_event.timestamp > self.state.timestamp:
                self.timing_event_index_by_car[car] += i
                return (previous_timing_event, timing_event)

            previous_timing_event = timing_event

        self.timing_event_index_by_car[car] += len(timing_events)
        return previous_timing_event, None

    def _find_current_stint(self, car_state: CarState) -> model.Stint:
        for stint in reversed(self.session.stints[car_state.car.number]):
            if stint.lap_start <= car_state.progress.lap:
                return stint
        assert False, f"no stint for car {car_state}"

    def _update_car_progress(self, car_state: CarState):
        assert car_state.previous_timing_event is not None
        if car_state.next_timing_event is None:
            # in case some events have been skipped, fill from most recent timing event
            car_state.progress.lap = car_state.previous_timing_event.sector.lap
            car_state.progress.sector = car_state.previous_timing_event.sector.sector
            car_state.progress.fraction = 1.0

            return

        car_state.progress.lap = car_state.next_timing_event.sector.lap
        car_state.progress.sector = car_state.next_timing_event.sector.sector

        sector_duration = (
            car_state.next_timing_event.timestamp
            - car_state.previous_timing_event.timestamp
        )
        since_sector_start = (
            self.state.timestamp - car_state.previous_timing_event.timestamp
        )
        car_state.progress.fraction = since_sector_start / sector_duration
