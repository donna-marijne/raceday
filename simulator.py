from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import log
import model


@dataclass
class Progress:
    lap: int
    sector: int
    fraction: float

    def __gt__(self, other):
        if self.lap > other.lap:
            return True

        if self.lap == other.lap:
            if self.sector > other.sector:
                return True

            if self.sector == other.sector:
                return self.fraction > other.fraction

        return False


@dataclass()
class CarState:
    car: model.Car
    previous_timing_event: Optional[model.TimingEvent]
    next_timing_event: Optional[model.TimingEvent]
    tyre_compound: model.TyreCompound
    tyre_age: int
    progress: Progress
    in_pit_lane: bool


@dataclass()
class State:
    session: model.Session
    timestamp: datetime
    cars: list[CarState]


class Simulator:
    def __init__(self, session: model.Session):
        self.session = session
        self.state = self._init_state()

    def advance(self, period: timedelta):
        new_timestamp = self.state.timestamp + period

        log.debug(f"Simulator.advance: {self.state.timestamp} -> {new_timestamp}")

        for car_state in self.state.cars:
            log.debug(f"car_state={car_state}")

            if car_state.next_timing_event is None:
                # car has retired, nothing more to do
                continue

            car_number = car_state.car.number
            new_timing_events = self._find_new_timing_events_for_car(
                car_number, after=self.state.timestamp, before=new_timestamp
            )

            log.debug(f"new_timing_events={new_timing_events}")

            # no new timing events means the car hasn't crossed a sector during the period
            if len(new_timing_events) > 0:
                # will this ever reasonably not be car_state.next_timing_event?
                # yes if we want to be able to skip to specific times in the session
                car_state.previous_timing_event = new_timing_events[-1]

            assert car_state.previous_timing_event is not None

            car_state.next_timing_event = self._find_next_timing_event_for_car(
                car_number, after=new_timestamp
            )

            timing_event = (
                car_state.next_timing_event or car_state.previous_timing_event
            )
            car_state.tyre_compound = timing_event.car_state.tyre_compound
            car_state.tyre_age = timing_event.car_state.tyre_age

            # TODO: how to determine in_pit_lane

            self._update_car_progress(car_state=car_state, timestamp=new_timestamp)

        self.state.cars.sort(key=lambda car_state: car_state.progress, reverse=True)
        self.state.timestamp = new_timestamp

        # log.debug(f"advance: state={self.state}")

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

    def _find_next_timing_event_for_car(
        self, car: int, after: datetime
    ) -> Optional[model.TimingEvent]:
        for timing_event in self.session.timing_events_by_car[car]:
            # collection should be in order so just return the first one
            if timing_event.timestamp > after:
                return timing_event

        return None

    def _update_car_progress(self, car_state: CarState, timestamp: datetime):
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
        since_sector_start = timestamp - car_state.previous_timing_event.timestamp
        car_state.progress.fraction = since_sector_start / sector_duration

        log.debug(
            f"_update_car_progress: timestamp={timestamp}, previous_timing_event={car_state.previous_timing_event}, next_timing_event={car_state.next_timing_event}"
        )
