import unittest
import data_access
from collections import namedtuple
from decimal import Decimal
from fozr_utils import DerbyUtil

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"


class DerbyUtilTestCase(unittest.TestCase):

    def setUp(self):
        pass

    @property
    def util(self):
        return DerbyUtil()

    def test_calc_round_num(self):
        self.assertEqual(1, self.util.calc_round_num(1, 5))
        self.assertEqual(1, self.util.calc_round_num(5, 5))
        self.assertEqual(2, self.util.calc_round_num(6, 5))
        self.assertEqual(10, self.util.calc_round_num(99, 10))
        self.assertEqual(10, self.util.calc_round_num(100, 10))
        self.assertEqual(11, self.util.calc_round_num(101, 10))

    def test_calc_heat_num(self):
        for i in range(1, 100 + 1):
            self.assertTrue(1 <= self.util.calc_heat_num(i, 7) <= 7)

        self.assertEqual(1, self.util.calc_heat_num(1, 5))
        self.assertEqual(5, self.util.calc_heat_num(5, 5))
        self.assertEqual(1, self.util.calc_heat_num(6, 5))
        self.assertEqual(9, self.util.calc_heat_num(99, 10))
        self.assertEqual(10, self.util.calc_heat_num(100, 10))
        self.assertEqual(1, self.util.calc_heat_num(101, 10))

    def test_convert_timer_data(self):
        data = "6 2.5854  7 2.5874  4 2.6130  5 2.6143  2 2.6717  1 2.7175  3 2.7606\r\n"
        PlaceLaneTime = namedtuple('PlaceLaneTime', 'place lane time')
        expected_results = [
            PlaceLaneTime(1, 6, Decimal('2.5854')),
            PlaceLaneTime(2, 7, Decimal('2.5874')),
            PlaceLaneTime(3, 4, Decimal('2.6130')),
            PlaceLaneTime(4, 5, Decimal('2.6143')),
            PlaceLaneTime(5, 2, Decimal('2.6717')),
            PlaceLaneTime(6, 1, Decimal('2.7175')),
            PlaceLaneTime(7, 3, Decimal('2.7606'))
        ]
        td = self.util.convert_timer_data(data)

        self.assertEqual(7, len(td))
        for i in range(0, 7):
            self.assertEqual(expected_results[i].place, td[i].place)
            self.assertEqual(expected_results[i].lane, td[i].lane)
            self.assertEqual(expected_results[i].time, td[i].time)

    def test_convert_timer_data_with_dnf(self):
        data = "2 2.5854  1 2.5874  0 0.0000  0 0.0000\r\n"
        td = self.util.convert_timer_data(data)
        self.assertEqual(4, len(td))
        self.assertEqual(3, td[2].place)
        self.assertEqual(0, td[2].lane)
        self.assertEqual(Decimal('0.0000'), td[2].time)

    def test_escape_sql_like_pattern(self):
        self.assertEqual("abc", self.util.escape_sql_like_pattern("abc"))
        self.assertEqual("[%]abc[%]", self.util.escape_sql_like_pattern("%abc%"))
        self.assertEqual("a[_]b[_]c[%]", self.util.escape_sql_like_pattern("a_b_c%"))
        self.assertEqual("a[[]bc]", self.util.escape_sql_like_pattern("a[bc]"))
        self.assertEqual("a[%][%]", self.util.escape_sql_like_pattern("a%%"))

    def generate_racers(self, num_racers, racing_class, starting_car_num=1):
        result = []
        for i in range(0, num_racers):
            result.append(data_access.Racer(i + starting_car_num, "car {0}".format(i + starting_car_num), racing_class))
        return result

    def test_get_race_round_details(self):
        scouts = data_access.RacingClass(1, "Scouts")
        family = data_access.RacingClass(2, "Family")
        ten_scouts = self.generate_racers(10, scouts)
        four_family = self.generate_racers(4, family, 100)
        three_scouts = self.generate_racers(3, scouts)

        tests = [
            {
                'racers': ten_scouts + four_family,
                'num_lanes': 5,
                'expected_results': [
                    {'group': 'Scouts', 'racers': ten_scouts, 'num_racers': 10, 'num_byes': 0, 'starting_heat': 1, 'heats_per_round': 2},
                    {'group': 'Family', 'racers': four_family, 'num_racers': 4, 'num_byes': 1, 'starting_heat': 3, 'heats_per_round': 1}
                ]
            },
            {
                'racers': three_scouts,
                'num_lanes': 7,
                'expected_results': [
                    {'group': 'Scouts', 'racers': three_scouts, 'num_racers': 3, 'num_byes': 4, 'starting_heat': 1, 'heats_per_round': 1},
                ]
            },
        ]

        for test in tests:
            racers = test['racers']
            num_lanes = test['num_lanes']
            expected_result = test['expected_results']
            actual_result = self.util.get_race_round_details(racers, num_lanes)
            self.assertEqual(expected_result, actual_result)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(DerbyUtilTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
