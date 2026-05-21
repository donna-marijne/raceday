from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import model


@dataclass
class Progress:
    lap: int
    sector: int
    fraction: float


@dataclass()
class CarState:
    car: model.Car
    previous_timing_event: model.TimingEvent | None
    next_timing_event: model.TimingEvent | None
    tyre_compound: model.TyreCompound
    tyre_age: int
    progress: Progress
    in_pit_lane: bool


@dataclass()
class State:
    session: model.Session
    timestamp: datetime
    cars: list[CarState]
    timing_event_index: int | None


class Simulator:
    def __init__(self, session: model.Session):
        self.session = session
        self.state = self._init_state()

    def advance(self, period: timedelta):
        new_timestamp = self.state.timestamp + period

        for car_state in self.state.cars:
            car_number = car_state.car.number
            new_timing_events = self._find_new_timing_events_for_car(
                car_number, self.state.timestamp, new_timestamp
            )
            previous_timing_event = new_timing_events[-1]
            next_timing_event = self._find_next_timing_event_for_car(car_number)

    def _init_state(self) -> State:
        car_states: list[CarState] = []
        for car_starting_state in self.session.starting_grid:
            car_number = car_starting_state.number
            car = self.session.cars[car_number]

            # fake timing event for race start
            previous_timing_event = model.TimingEvent(
                timestamp=self.session.start,
                sector=model.Sector(lap=1, sector=1),
                sector_duration=None,
                car=car,
                car_state=model.CarState(
                    number=car_number,
                    position=-1,
                    tyre_age=car_starting_state.tyre_age,
                    tyre_compound=car_starting_state.tyre_compound,
                ),
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
                tyre_compound=car_starting_state.tyre_compound,
                tyre_age=car_starting_state.tyre_age,
                progress=Progress(lap=1, sector=1, fraction=0.0),
                in_pit_lane=False,
            )
            car_states.append(car_state)

        state = State(
            session=self.session,
            timestamp=self.session.start,
            cars=car_states,
            timing_event_index=0,
        )

        return state

    def _find_new_timing_events_for_car(
        self, car: int, after: datetime, before: datetime
    ) -> list[model.TimingEvent]:
        new_timing_events: list[model.TimingEvent] = []
        for timing_event in self.session.timing_events_by_car[car]:
            if timing_event.timestamp > before:
                break
            if timing_event.timestamp > after:
                new_timing_events.append(timing_event)

        return new_timing_events

    def _find_next_timing_event_for_car(self, car: int) -> Optional[model.TimingEvent]:
        for timing_event in self.session.timing_events_by_car[car]:
            # collection should be in order so just return the first one
            if timing_event.timestamp > self.state.timestamp:
                return timing_event

        return None
