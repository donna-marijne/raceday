import json
import unittest
from pathlib import Path

import model
from openf1.openf1_payload import OpenF1Payload
from openf1.timing_events import timing_events_from_api


def _create_test_payload(laps):
    return OpenF1Payload(
        drivers=[],
        laps=laps,
        meeting={},
        pit=[],
        qualifying_laps=[],
        session={},
        starting_grid=[],
        stints=[],
    )


class TestTimingEventsFromJson(unittest.TestCase):
    def setUp(self):
        self.test_data_dir_path = Path(__file__).parent / "data" / "laps"
        self.cars = {
            11: model.Car(
                number=11,
                driver_name="Sergio PEREZ",
                driver_acronym="PER",
                team_name="Red Bull Racing",
                color="3671C6",
            ),
            44: model.Car(
                number=44,
                driver_name="Lewis HAMILTON",
                driver_acronym="HAM",
                team_name="Mercedes",
                color="27F4D2",
            ),
        }
        self.stints = {
            11: [
                model.Stint(
                    number=1,
                    car_number=11,
                    lap_start=1,
                    tyre_compound=model.TyreCompound("MEDIUM"),
                    tyre_age_at_start=3,
                )
            ],
            44: [
                model.Stint(
                    number=1,
                    car_number=44,
                    lap_start=1,
                    tyre_compound=model.TyreCompound("MEDIUM"),
                    tyre_age_at_start=3,
                )
            ],
        }

    def test_single(self):
        file_path = self.test_data_dir_path / "single.json"
        laps = None
        with file_path.open("r") as file:
            json_str = file.read()
            laps = json.loads(json_str)

        events = timing_events_from_api(_create_test_payload(laps), cars=self.cars)
        self.assertEqual(len(events), 3)
        self.assertEqual(
            events[0].timestamp.isoformat(),
            "2024-07-28T13:04:27.080000+00:00",
        )
        self.assertEqual(events[0].sector, model.Sector(1, 1))
        self.assertEqual(events[0].car.number, 11)
        self.assertEqual(
            events[1].timestamp.isoformat(),
            "2024-07-28T13:05:17.118000+00:00",
        )
        self.assertEqual(events[1].sector, model.Sector(1, 2))
        self.assertEqual(events[1].car.number, 11)
        self.assertEqual(
            events[2].timestamp.isoformat(),
            "2024-07-28T13:05:46.609000+00:00",
        )
        self.assertEqual(events[2].sector, model.Sector(1, 3))
        self.assertEqual(events[2].car.number, 11)

    def test_two_cars_one_lap(self):
        file_path = self.test_data_dir_path / "two_cars_one_lap.json"
        laps = None
        with file_path.open("r") as file:
            json_str = file.read()
            laps = json.loads(json_str)
        events = timing_events_from_api(_create_test_payload(laps), cars=self.cars)
        self.assertEqual(len(events), 6)
        # car 44 lap 1 sector 1
        self.assertEqual(
            events[0].timestamp.isoformat(),
            "2024-07-28T13:04:26.998000+00:00",
        )
        self.assertEqual(events[0].sector, model.Sector(1, 1))
        self.assertEqual(events[0].car.number, 44)
        # car 11 lap 1 sector 1
        self.assertEqual(
            events[1].timestamp.isoformat(),
            "2024-07-28T13:04:27.080000+00:00",
        )
        self.assertEqual(events[1].sector, model.Sector(1, 1))
        self.assertEqual(events[1].car.number, 11)
        # car 44 lap 1 sector 2
        self.assertEqual(
            events[2].timestamp.isoformat(),
            "2024-07-28T13:05:16.404000+00:00",
        )
        self.assertEqual(events[2].sector, model.Sector(1, 2))
        self.assertEqual(events[2].car.number, 44)
        # car 11 lap 1 sector 2
        self.assertEqual(
            events[3].timestamp.isoformat(),
            "2024-07-28T13:05:17.118000+00:00",
        )
        self.assertEqual(events[3].sector, model.Sector(1, 2))
        self.assertEqual(events[3].car.number, 11)
        # car 44 lap 1 sector 3
        self.assertEqual(
            events[4].timestamp.isoformat(),
            "2024-07-28T13:05:45.882000+00:00",
        )
        self.assertEqual(events[4].sector, model.Sector(1, 3))
        self.assertEqual(events[4].car.number, 44)
        # car 11 lap 1 sector 3
        self.assertEqual(
            events[5].timestamp.isoformat(),
            "2024-07-28T13:05:46.609000+00:00",
        )
        self.assertEqual(events[5].sector, model.Sector(1, 3))
        self.assertEqual(events[5].car.number, 11)


if __name__ == "__main__":
    unittest.main()
