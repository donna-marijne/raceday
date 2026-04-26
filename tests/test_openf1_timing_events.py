import json
import unittest
from pathlib import Path

from car import Car
from openf1.timing_events import timing_events_from_api_laps
from sector import Sector


class TestTimingEventsFromJson(unittest.TestCase):
    def setUp(self):
        self.test_data_dir_path = Path(__file__).parent / "data"
        self.cars = {
            11: Car(
                number=11,
                driver_name="Sergio PEREZ",
                driver_acronym="PER",
                team_name="Red Bull Racing",
                color="3671C6",
            ),
            44: Car(
                number=44,
                driver_name="Lewis HAMILTON",
                driver_acronym="HAM",
                team_name="Mercedes",
                color="27F4D2",
            ),
        }

    def test_single(self):
        file_path = self.test_data_dir_path / "single.json"
        laps = None
        with file_path.open("r") as file:
            json_str = file.read()
            laps = json.loads(json_str)

        events = timing_events_from_api_laps(laps, self.cars)
        self.assertEqual(len(events), 3)
        self.assertEqual(
            events[0].timestamp.isoformat(),
            "2024-07-28T13:04:27.080000+00:00",
        )
        self.assertEqual(events[0].sector, Sector(1, 1))
        self.assertEqual(events[0].car.number, 11)
        self.assertEqual(events[0].car_position, 1)
        self.assertEqual(
            events[1].timestamp.isoformat(),
            "2024-07-28T13:05:17.118000+00:00",
        )
        self.assertEqual(events[1].sector, Sector(1, 2))
        self.assertEqual(events[1].car.number, 11)
        self.assertEqual(events[1].car_position, 1)
        self.assertEqual(
            events[2].timestamp.isoformat(),
            "2024-07-28T13:05:46.609000+00:00",
        )
        self.assertEqual(events[2].sector, Sector(1, 3))
        self.assertEqual(events[2].car.number, 11)
        self.assertEqual(events[2].car_position, 1)

    def test_two_cars_one_lap(self):
        file_path = self.test_data_dir_path / "two_cars_one_lap.json"
        laps = None
        with file_path.open("r") as file:
            json_str = file.read()
            laps = json.loads(json_str)
        events = timing_events_from_api_laps(laps, self.cars)
        self.assertEqual(len(events), 6)
        # car 44 lap 1 sector 1
        self.assertEqual(
            events[0].timestamp.isoformat(),
            "2024-07-28T13:04:26.998000+00:00",
        )
        self.assertEqual(events[0].sector, Sector(1, 1))
        self.assertEqual(events[0].car.number, 44)
        self.assertEqual(events[0].car_position, 1)
        # car 11 lap 1 sector 1
        self.assertEqual(
            events[1].timestamp.isoformat(),
            "2024-07-28T13:04:27.080000+00:00",
        )
        self.assertEqual(events[1].sector, Sector(1, 1))
        self.assertEqual(events[1].car.number, 11)
        self.assertEqual(events[1].car_position, 2)
        # car 44 lap 1 sector 2
        self.assertEqual(
            events[2].timestamp.isoformat(),
            "2024-07-28T13:05:16.404000+00:00",
        )
        self.assertEqual(events[2].sector, Sector(1, 2))
        self.assertEqual(events[2].car.number, 44)
        self.assertEqual(events[2].car_position, 1)
        # car 11 lap 1 sector 2
        self.assertEqual(
            events[3].timestamp.isoformat(),
            "2024-07-28T13:05:17.118000+00:00",
        )
        self.assertEqual(events[3].sector, Sector(1, 2))
        self.assertEqual(events[3].car.number, 11)
        self.assertEqual(events[3].car_position, 2)
        # car 44 lap 1 sector 3
        self.assertEqual(
            events[4].timestamp.isoformat(),
            "2024-07-28T13:05:45.882000+00:00",
        )
        self.assertEqual(events[4].sector, Sector(1, 3))
        self.assertEqual(events[4].car.number, 44)
        self.assertEqual(events[4].car_position, 1)
        # car 11 lap 1 sector 3
        self.assertEqual(
            events[5].timestamp.isoformat(),
            "2024-07-28T13:05:46.609000+00:00",
        )
        self.assertEqual(events[5].sector, Sector(1, 3))
        self.assertEqual(events[5].car.number, 11)
        self.assertEqual(events[5].car_position, 2)


if __name__ == "__main__":
    unittest.main()
