"""
Defines tests for derby
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

import os
from tests import settings_test
from factories import FozrFactory
from FiveOzRacer import Derby
from pprint import pprint
from config import Config
import unittest

Config.settings = settings_test.settings_test


class DerbyTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = FozrFactory()

        # prepare derby
        derby = Derby(self.factory)
        racers_filepath = os.path.join(self.factory.settings['INIT_DATA_PATH'], 'racers.csv')
        du = self.factory.create_data_util()
        racer_data = du.get_data_from_file(racers_filepath)
        derby.prepare_derby(racer_data, 2, 2)

    def tearDown(self):
        pass

    def get_derby(self):
        derby = Derby()
        derby.load()
        return derby

    def test_load(self):
        self.get_derby()

    def test_get_last_race_result(self):
        derby = self.get_derby()
        result = derby.get_last_race_result()

    def test_get_currently_racing(self):
        derby = self.get_derby()
        result = derby.get_currently_racing()

    def test_get_on_deck(self):
        derby = self.get_derby()
        result = derby.get_on_deck()

if __name__ == '__main__':
    unittest.main()
