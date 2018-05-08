"""
Defines tests for derby
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

import os
from tests import settings_test
from factories import FozrFactory
from FiveOzRacer import Derby
fozr_factory = FozrFactory(settings_test.settings_test)
from pprint import pprint
import unittest


class DerbyTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = fozr_factory
        self.derby = Derby(fozr_factory)

    def tearDown(self):
        pass

    def test_prepare_derby(self):
        racers_filepath = os.path.join(self.factory.settings['INIT_DATA_PATH'], 'racers.csv')
        du = fozr_factory.create_data_util()
        racer_data = du.get_data_from_file(racers_filepath)
        self.derby.prepare_derby(racer_data, 2, 2)

    def test_load(self):
        self.derby.load()

if __name__ == '__main__':
    unittest.main()
