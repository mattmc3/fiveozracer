import sys
import os
import re
import sqlite3
from FiveOzRacer import Derby
from factories import FozrFactory
from tests import settings_test
from config import Config
#Config.settings = settings_test.settings_test

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"


def main():
    sure = input("This will delete all records from the timer_data table. Are you sure [Y/n]?")
    if sure != "Y":
        print("Exiting...")
        sys.exit()

    factory = FozrFactory()

    # reset database
    with sqlite3.connect(Config.settings['DATABASE_PATH']) as conn:
        conn.execute('delete from timer_data')
        conn.execute('delete from race_results')
        conn.execute('update derby_details set race_number = 1')
    #du = factory.create_data_util()
    #du.init_db()

    #racers_filepath = os.path.join(factory.settings['INIT_DATA_PATH'], 'racers.csv')
    #du = factory.create_data_util()
    #racer_data = du.get_data_from_file(racers_filepath)

    derby = Derby()
    #derby.prepare_derby(racer_data, 2, 2)
    derby.load()
    derby.sort_for_round()

    print("Press 'q' to quit. 'a' for All. ENTER to add timer records one at a time")
    all_mode = False
    for data in iter_timer_results():
        if not all_mode:
            val = input("")

        if val.lower() == 'q':
            sys.exit()
        elif val.lower() == 'a':
            all_mode = True

        print(data.strip())

        derby = Derby()
        derby.load()
        derby.log_timer_data(data)


def iter_timer_results():
    filename = "db_test/timer_data.txt"
    with open(filename, "r") as infile:
        for line in infile:
            line = re.sub(r'\s*\#.*$', '', line)
            line = line.strip()
            if len(line) > 0 and line != "DT8000  NewBold Products" and line[0] != "#":
                yield line


if __name__ == "__main__":
    main()
