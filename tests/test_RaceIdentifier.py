import unittest
from collections import namedtuple
from decimal import Decimal
from FiveOzRacer import RaceIdentifier

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"


class RaceIdentifierTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_calc_round_num(self):
        self.assertEqual(1, RaceIdentifier(1, 5).round_number)
        self.assertEqual(1, RaceIdentifier(5, 5).round_number)
        self.assertEqual(2, RaceIdentifier(6, 5).round_number)
        self.assertEqual(10, RaceIdentifier(99, 10).round_number)
        self.assertEqual(10, RaceIdentifier(100, 10).round_number)
        self.assertEqual(11, RaceIdentifier(101, 10).round_number)

    def test_calc_heat_num(self):
        for i in range(1, 100 + 1):
            self.assertTrue(1 <= RaceIdentifier(i, 7).heat_number <= 7)

        self.assertEqual(1, RaceIdentifier(1, 5).heat_number)
        self.assertEqual(5, RaceIdentifier(5, 5).heat_number)
        self.assertEqual(1, RaceIdentifier(6, 5).heat_number)
        self.assertEqual(9, RaceIdentifier(99, 10).heat_number)
        self.assertEqual(10, RaceIdentifier(100, 10).heat_number)
        self.assertEqual(1, RaceIdentifier(101, 10).heat_number)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(RaceIdentifierTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
