import sys
import os
import sqlite3
import logging
from FiveOzRacer import Derby
from factories import FozrFactory
from config import Config


def main():
    res = input('WARNING: The fozr database is about to be reset.  Proceed [Y/n]?')
    if res != 'Y':
        print('Exiting with no further action.')
        sys.exit()

    #logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

    factory = FozrFactory()

    # reset database
    with sqlite3.connect(Config.settings['DATABASE_PATH']) as conn:
        conn.execute('delete from timer_data')
        conn.execute('delete from race_results')
    du = factory.create_data_util()
    du.init_db()

    racers_filepath = os.path.join(factory.settings['INIT_DATA_PATH'], 'racers.csv')
    du = factory.create_data_util()
    racer_data = du.get_data_from_file(racers_filepath)

    derby = Derby()
    lanes = 7
    heats = 7
    derby.prepare_derby(racer_data, lanes, heats)
    derby.load()

if __name__ == '__main__':
    main()
