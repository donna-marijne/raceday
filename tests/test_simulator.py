import unittest
from copy import copy
from datetime import datetime, timedelta

import model
from simulator import Progress, Simulator


def _generate_timing_event(
    previous: model.TimingEvent, duration: timedelta
) -> model.TimingEvent:
    timing_event = model.TimingEvent(
        car=previous.car,
        car_state=copy(previous.car_state),
        sector=previous.sector.next(),
        sector_duration=None,
        timestamp=previous.timestamp + duration,
    )
    if timing_event.sector.sector == 1:
        timing_event.car_state.tyre_age += 1

    return timing_event


def _generate_timing_events_for_car(
    car: model.Car, car_state: model.CarState, start: datetime, durations: list[float]
) -> list[model.TimingEvent]:
    previous_event = None
    timing_events = []
    for duration in durations:
        if previous_event is None:
            timing_event = model.TimingEvent(
                timestamp=start + timedelta(seconds=duration),
                sector=model.Sector(lap=1, sector=1),
                sector_duration=None,
                car=car,
                car_state=car_state,
            )
        else:
            timing_event = _generate_timing_event(
                previous=previous_event, duration=timedelta(seconds=duration)
            )

        timing_events.append(timing_event)
        previous_event = timing_event

    return timing_events


def _merge_timing_events_by_car(
    timing_events_by_car: dict[int, list[model.TimingEvent]],
) -> list[model.TimingEvent]:
    merged_timing_events = []
    for timing_events in timing_events_by_car.values():
        merged_timing_events.extend(timing_events)

    return sorted(merged_timing_events, key=lambda timing_event: timing_event.timestamp)


class TestSimulator(unittest.TestCase):

    def assertProgressEqual(self, one: Progress, two: Progress, msg=None):
        self.assertEqual(one.lap, two.lap, msg=msg)
        self.assertEqual(one.sector, two.sector, msg=msg)
        self.assertAlmostEqual(one.fraction, two.fraction, places=3, msg=msg)

    def test_two_laps_with_overtake(self):
        cars: dict[int, model.Car] = {
            11: model.Car(
                number=11,
                driver_name="Sergio PEREZ",
                driver_acronym="PER",
                team_name="Cadillac",
                color="909090",
            ),
            44: model.Car(
                number=44,
                driver_name="Lewis HAMILTON",
                driver_acronym="HAM",
                team_name="Ferrari",
                color="ED1131",
            ),
        }

        starting_grid: list[model.CarState] = [
            model.CarState(
                number=11,
                position=-1,
                tyre_age=0,
                tyre_compound=model.TyreCompound.INTERMEDIATE,
            ),
            model.CarState(
                number=44,
                position=-1,
                tyre_age=3,
                tyre_compound=model.TyreCompound.SOFT,
            ),
        ]

        start = datetime.fromisoformat("2026-05-21T14:16:00Z")

        timing_events_by_car: dict[int, list[model.TimingEvent]] = {
            11: _generate_timing_events_for_car(
                car=cars[11],
                car_state=starting_grid[0],
                start=start,
                durations=[28, 26, 43, 19, 25, 44],
            ),
            44: _generate_timing_events_for_car(
                car=cars[44],
                car_state=starting_grid[1],
                start=start,
                durations=[27, 24, 42, 19, 24, 41],
            ),
        }

        session = model.Session(
            name="2026 Unit Testing Grand Prix",
            cars=cars,
            sector_split=(0.2, 0.3, 0.5),
            start=start,
            starting_grid=starting_grid,
            timing_events=_merge_timing_events_by_car(timing_events_by_car),
            timing_events_by_car=timing_events_by_car,
            total_laps=2,
        )

        simulator = Simulator(session)

        state = simulator.state

        self.assertEqual(state.timestamp, start)

        self.assertEqual(state.cars[0].car.number, 11)
        self.assertIsNotNone(state.cars[0].previous_timing_event)
        self.assertIsNotNone(state.cars[0].next_timing_event)
        self.assertProgressEqual(
            state.cars[0].progress, Progress(lap=1, sector=1, fraction=0.0)
        )
        self.assertEqual(state.cars[0].tyre_age, 0)
        self.assertEqual(state.cars[0].tyre_compound, model.TyreCompound.INTERMEDIATE)

        self.assertEqual(state.cars[1].car.number, 44)
        self.assertIsNotNone(state.cars[1].previous_timing_event)
        self.assertIsNotNone(state.cars[1].next_timing_event)
        self.assertProgressEqual(
            state.cars[1].progress, Progress(lap=1, sector=1, fraction=0.0)
        )
        self.assertEqual(state.cars[1].tyre_age, 3)
        self.assertEqual(state.cars[1].tyre_compound, model.TyreCompound.SOFT)

        # move forward one frame
        simulator.advance(timedelta(seconds=1 / 30))

        self.assertGreater(state.timestamp, start)

        self.assertEqual(state.cars[0].car.number, 44)
        self.assertProgressEqual(
            state.cars[0].progress, Progress(lap=1, sector=1, fraction=0.001)
        )
        self.assertEqual(state.cars[0].tyre_age, 3)
        self.assertEqual(state.cars[0].tyre_compound, model.TyreCompound.SOFT)

        self.assertEqual(state.cars[1].car.number, 11)
        self.assertProgressEqual(
            state.cars[1].progress, Progress(lap=1, sector=1, fraction=0.001)
        )
        self.assertEqual(state.cars[1].tyre_age, 0)
        self.assertEqual(state.cars[1].tyre_compound, model.TyreCompound.INTERMEDIATE)

        # move forward 30 seconds (30 * 30 frames)
        for _ in range(30 * 30):
            simulator.advance(timedelta(seconds=1 / 30))

        self.assertGreater(state.timestamp, start + timedelta(seconds=30))
        self.assertLess(state.timestamp, start + timedelta(seconds=31))

        self.assertEqual(state.cars[0].car.number, 44)
        self.assertProgressEqual(
            state.cars[0].progress, Progress(lap=1, sector=2, fraction=0.126)
        )
        self.assertEqual(state.cars[0].tyre_age, 3)
        self.assertEqual(state.cars[0].tyre_compound, model.TyreCompound.SOFT)

        self.assertEqual(state.cars[1].car.number, 11)
        self.assertProgressEqual(
            state.cars[1].progress, Progress(lap=1, sector=2, fraction=0.078)
        )
        self.assertEqual(state.cars[1].tyre_age, 0)
        self.assertEqual(state.cars[1].tyre_compound, model.TyreCompound.INTERMEDIATE)

        # move forward 75 seconds in one step
        simulator.advance(timedelta(seconds=75))

        self.assertGreater(state.timestamp, start + timedelta(seconds=105))

        self.assertEqual(state.cars[0].car.number, 44)
        self.assertProgressEqual(
            state.cars[0].progress, Progress(lap=2, sector=1, fraction=0.633)
        )
        self.assertEqual(state.cars[0].tyre_age, 4)
        self.assertEqual(state.cars[0].tyre_compound, model.TyreCompound.SOFT)

        self.assertEqual(state.cars[1].car.number, 11)
        self.assertProgressEqual(
            state.cars[1].progress, Progress(lap=2, sector=1, fraction=0.423)
        )
        self.assertEqual(state.cars[1].tyre_age, 1)
        self.assertEqual(state.cars[1].tyre_compound, model.TyreCompound.INTERMEDIATE)

        # move forward another 100 seconds (end of race)
        simulator.advance(timedelta(seconds=100))

        self.assertGreater(state.timestamp, start + timedelta(seconds=205))

        self.assertEqual(state.cars[0].car.number, 44)
        self.assertProgressEqual(
            state.cars[0].progress, Progress(lap=2, sector=3, fraction=1.0)
        )
        self.assertEqual(state.cars[0].tyre_age, 4)
        self.assertEqual(state.cars[0].tyre_compound, model.TyreCompound.SOFT)

        self.assertEqual(state.cars[1].car.number, 11)
        self.assertProgressEqual(
            state.cars[1].progress, Progress(lap=2, sector=3, fraction=1.0)
        )
        self.assertEqual(state.cars[1].tyre_age, 1)
        self.assertEqual(state.cars[1].tyre_compound, model.TyreCompound.INTERMEDIATE)
