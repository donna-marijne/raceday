import unittest
from pathlib import Path

from openf1.session import session_from_source_dir


class TestOpenF1SessionFromSourceDir(unittest.TestCase):
    def setUp(self):
        self.test_data_dir_path = Path(__file__).parent / "data" / "payloads"

    def test_2024_belgium(self):
        dir_path = self.test_data_dir_path / "9574"
        session = session_from_source_dir(dir_path)

        self.assertEqual(session.name, "2024 Belgian Grand Prix")
        self.assertEqual(session.total_laps, 44)
        self.assertEqual(len(session.cars), 20)
        self.assertIn(44, session.cars)
        self.assertIn(24, session.cars)
        self.assertIn(63, session.cars)
        self.assertEqual(session.cars[1].driver_acronym, "VER")
        self.assertEqual(len(session.starting_grid), 20)
        self.assertEqual(session.starting_grid[0], 16)
        self.assertEqual(session.starting_grid[1], 11)
        self.assertEqual(session.starting_grid[10], 1)
        self.assertEqual(session.starting_grid[18], 24)
        self.assertEqual(session.starting_grid[19], 22)
        self.assertEqual(len(session.timing_events), 2523)

    def test_2025_singapore(self):
        dir_path = self.test_data_dir_path / "9896"
        session = session_from_source_dir(dir_path)

        self.assertEqual(session.name, "2025 Singapore Grand Prix")
        self.assertEqual(session.total_laps, 62)
        self.assertEqual(len(session.cars), 20)
        self.assertIn(63, session.cars)
        self.assertIn(10, session.cars)
        self.assertIn(23, session.cars)
        self.assertEqual(session.cars[1].driver_acronym, "VER")
        self.assertEqual(len(session.starting_grid), 20)
        self.assertEqual(session.starting_grid[0], 63)
        self.assertEqual(session.starting_grid[1], 1)
        self.assertEqual(session.starting_grid[17], 10)
        self.assertEqual(session.starting_grid[18], 55)
        self.assertEqual(session.starting_grid[19], 23)
        self.assertEqual(len(session.timing_events), 3687)

    def test_2026_china(self):
        dir_path = self.test_data_dir_path / "11245"
        session = session_from_source_dir(dir_path)

        self.assertEqual(session.name, "2026 Chinese Grand Prix")
        self.assertEqual(session.total_laps, 56)
        self.assertEqual(len(session.cars), 22)
        self.assertIn(63, session.cars)
        self.assertIn(1, session.cars)
        self.assertIn(77, session.cars)
        self.assertEqual(session.cars[1].driver_acronym, "NOR")
        self.assertEqual(len(session.starting_grid), 22)
        self.assertEqual(session.starting_grid[0], 12)
        self.assertEqual(session.starting_grid[1], 63)
        self.assertEqual(session.starting_grid[4], 81)
        self.assertEqual(session.starting_grid[17], 14)
        self.assertEqual(session.starting_grid[20], 11)
        self.assertEqual(session.starting_grid[21], 23)
        self.assertEqual(len(session.timing_events), 2757)

    def test_2026_china_sprint(self):
        dir_path = self.test_data_dir_path / "11240"
        session = session_from_source_dir(dir_path)

        self.assertEqual(session.name, "2026 Chinese Grand Prix")
        self.assertEqual(session.total_laps, 19)
        self.assertEqual(len(session.cars), 22)
        self.assertIn(63, session.cars)
        self.assertIn(1, session.cars)
        self.assertIn(77, session.cars)
        self.assertEqual(session.cars[1].driver_acronym, "NOR")
        self.assertEqual(len(session.starting_grid), 22)
        self.assertEqual(session.starting_grid[0], 63)
        self.assertEqual(session.starting_grid[1], 12)
        self.assertEqual(session.starting_grid[2], 1)
        self.assertEqual(session.starting_grid[19], 77)
        self.assertEqual(session.starting_grid[20], 11)
        self.assertEqual(session.starting_grid[21], 23)
        self.assertEqual(len(session.timing_events), 1188)
