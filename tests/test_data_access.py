import os
from config import Config
from tests import settings_test
from factories import FozrFactory
from pprint import pprint
import unittest

Config.settings = settings_test.settings_test


class DataAccessTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = FozrFactory()
        du = self.factory.create_data_util()
        du.init_db()

    def tearDown(self):
        pass

    def test_reload_racers(self, racers_filename="racers.csv"):
        racers_filepath = os.path.join(self.factory.settings['INIT_DATA_PATH'], racers_filename)
        du = self.factory.create_data_util()
        racer_data = du.get_data_from_file(racers_filepath)
        with self.factory.create_unit_of_work().begin() as uow:
            uow.racer_repository.reload_racers(racer_data)


    # def do_test_derby_setup(self, racers_filename="racers.csv", lanes_enabled=2):
    #     racers_filepath = os.path.join(self.settings['INIT_DATA_PATH'], racers_filename)
    #     self.repo.do_derby_setup(racers_filepath, lanes_enabled)
    #
    # def test_byes(self):
    #     # change defaults
    #     settings = self.settings.copy()
    #     settings['DERBIES_DATA'] = os.path.join(settings['INIT_DATA_PATH'], 'derbies2.csv')
    #     settings['RACERS_DATA'] = os.path.join(settings['INIT_DATA_PATH'], 'racers2.csv')
    #     factory = FozrFactory(settings=settings)
    #     repo = factory.create_derby_repository()
    #     repo.init_db()
    #
    #     repo.load_racers_from_file(settings['RACERS_DATA'])
    #     repo.create_byes()
    #     session = repo.get_session()
    #     racers = session.query(Racer).filter(Racer.bye_num == None).all()
    #     bye_racers = session.query(Racer).filter(Racer.bye_num != None).all()
    #
    #     self.assertEquals(17, len(racers))
    #     self.assertEquals(3, len(bye_racers))
    #     for r in bye_racers:
    #         self.assertEquals('Bye', r.driver_name[0:3])
    #     self.assertEquals('Scouts', bye_racers[0].racing_class.name)
    #     self.assertEquals(1, bye_racers[0].bye.heat_num)
    #     self.assertEquals(4, bye_racers[0].bye.lane_num)
    #     self.assertEquals('Scouts', bye_racers[1].racing_class.name)
    #     self.assertEquals(2, bye_racers[1].bye.heat_num)
    #     self.assertEquals(4, bye_racers[1].bye.lane_num)
    #     self.assertEquals('Adults', bye_racers[2].racing_class.name)
    #     self.assertEquals(5, bye_racers[2].bye.heat_num)
    #     self.assertEquals(4, bye_racers[2].bye.lane_num)
    #
    # def test_get_first_round_lineup_order(self):
    #     self.do_test_derby_setup()
    #     results = self.repo.get_round_lineup()
    #     self.assertEquals(3, len(results))
    #     for item in results:
    #         self.assertEquals(0, item['race_count'])
    #         self.assertEquals(0.0, item['total_time'])
    #     session = self.repo.get_session()
    #
    # # def test_get_first_round_lineup_order(self):
    # #     self.do_test_derby_setup(racers_filename="racers2.csv", lanes_enabled=4)
    # #     results = self.repo.get_round_lineup(1)
    # #     self.assertEquals(17, len(results))
    # #     for item in results:
    # #         self.assertEquals(0, item['race_count'])
    # #         self.assertEquals(0.0, item['total_time'])
    #
    # def test_load_lineup_for_round(self):
    #     self.do_test_derby_setup()
    #     self.repo.sort_for_round(1)

if __name__ == '__main__':
    unittest.main()
