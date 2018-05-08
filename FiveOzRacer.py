"""
Define domain models for FiveOzRacer
"""

import os
import math
import re
import logging
from decimal import Decimal
from asq.initiators import query as asquery
from common import Utils
from exceptions import FozrException
from data_access import Bye, DerbyDetail, Grade, RaceResult, Racer, RacingClass, StringTranslation, TimerData
from factories import FozrFactory
from config import Config
from collections import namedtuple
from pprint import pprint

# set globals
utils = Utils()


class Derby:
    name = None
    derby_date = None
    notes = None
    _heats_per_round = None
    _lanes_enabled = None
    _race_number = None
    _racers = None

    def __init__(self, factory=None):
        if factory is None:
            factory = FozrFactory()
        self.factory = factory

    @property
    def heats_per_round(self):
        return self._heats_per_round

    @property
    def lanes_enabled(self):
        return self._lanes_enabled

    @property
    def current_race(self):
        return self._race_number

    @property
    def current_round(self):
        return self.race_identifier.round_number

    @property
    def current_heat(self):
        return self.race_identifier.heat_number

    @property
    def racers(self):
        if self._racers is None:
            with self.factory.session_scope() as session:
                self._racers = asquery(session.query(Racer).all())\
                    .order_by(lambda r: r.racing_class_id)\
                    .then_by(lambda r: r.car_number)
        return self._racers

    @property
    def race_identifier(self):
        return RaceIdentifier(self._race_number, self._heats_per_round)

    def _new_uow(self):
        return self.factory.create_unit_of_work().begin()

    def load(self):
        """
        Loads the derby data from the data store
        """
        with self._new_uow() as uow:
            derby_detail = uow.derby_detail_repository.get_only_derby_detail()
            self.name = derby_detail.name
            self.derby_date = derby_detail.derby_date
            self.notes = derby_detail.notes
            self._race_number = derby_detail.race_number
            self._heats_per_round = derby_detail.heats_per_round
            self._lanes_enabled = derby_detail.lanes_enabled

    def prepare_derby(self, racers, lanes_enabled, heats_per_round):
        with self._new_uow() as uow:
            # clear race tables
            uow.timer_data_repository.delete_all()
            uow.race_result_repository.delete_all()
            uow.bye_repository.delete_all()

            # set derby detail
            derby_detail = uow.derby_detail_repository.get_only_derby_detail()
            derby_detail.lanes_enabled = lanes_enabled
            derby_detail.heats_per_round = heats_per_round
            derby_detail.race_number = 0

            # set racers
            uow.racer_repository.reload_racers(racers)

            # create byes
            bye_num = 0
            new_racers = uow.racer_repository.all()
            race_details = self.factory.create_derby_util().get_race_round_details(new_racers, lanes_enabled)

            for detail in race_details:
                bye_racing_class = uow.racing_class_repository.get_by_name(detail['group'])
                for bye_counter in range(0, detail['num_byes']):
                    bye_num += 1
                    heat_num = (bye_counter % detail['heats_per_round']) + detail['starting_heat']
                    lane_num = lanes_enabled - (bye_counter // detail['heats_per_round'])

                    bye = Bye(bye_num, heat_num, lane_num)
                    bye_racer = Racer(bye_num + 5550, "[BYE] {0} #{1}".format(detail['group'], bye_num), bye_racing_class, grade=None, bye=bye)
                    uow.racer_repository.add(bye_racer)

            uow.commit()
            self.load()

        self._prepare_next_race()

    def get_last_race_result(self):
        results = self.get_race_lineup(self.current_race - 1)
        results = asquery(results).order_by(lambda x: x.place).to_list()
        return results

    def get_currently_racing(self):
        return self.get_race_lineup(self.current_race)

    def get_on_deck(self):
        return self.get_race_lineup(self.current_race + 1)

    def get_race_lineup(self, race_number):
        with self._new_uow() as uow:
            results = uow.race_result_repository.get_race_lineup(race_number)
        return results

    def log_timer_data(self, raw_timer_data):
        with self._new_uow() as uow:
            timer = Timer()
            timer_data = timer.log_timer_data(raw_timer_data)
            uow.timer_data_repository.add(timer_data)

            race_results = uow.race_result_repository.get_race_results_by_race_number(self.current_race)
            lane_results = {x.lane: x for x in timer_data.lane_results}

            for rr in race_results:
                timer_result = lane_results.get(rr.lane_number)
                rr.timer_data = timer_data
                if timer_result is None:
                    # DNF
                    rr.time = Decimal("6.0000")
                    rr.place = len(race_results)
                else:
                    rr.time = Decimal(timer_result.time)
                    rr.place = timer_result.place
            uow.commit()

        self._prepare_next_race()
        self.load()

    def _prepare_next_race(self):
        """
        Advance to the next race
        """
        with self._new_uow() as uow:
            dd = uow.derby_detail_repository.get_only_derby_detail()
            dd.race_number += 1
            uow.commit()
            self.load()

        if self.current_heat == 1:
            self.sort_for_round()

        self.load()

    def sort_for_round(self):
        if self.current_heat != 1:
            raise FozrException("You may not sort for round unless it's the first heat. Current heat := {0}".format(self.current_race))

        with self._new_uow() as uow:
            is_round_already_calculated = uow.race_result_repository.is_round_lineup_calculated(self.current_round)
            if is_round_already_calculated:
                raise FozrException("You may not sort for round because the round was already calculated")

        race_num = self.current_race
        round_num = self.current_round
        with self._new_uow() as uow:
            byes = uow.racer_repository.get_bye_racers()
            non_bye_racers = uow.racer_repository.get_non_bye_racers()

            racers_lookup = self.factory.create_derby_util().get_lookup(non_bye_racers, lambda x: x.car_number)
            derby_standings = self.get_derby_standings()
            #derby_standings = derby_standings[::-1] #reverse
            racer_index = 0
            bye_index = 0
            next_bye = lambda: byes[bye_index] if len(byes) > bye_index else None
            next_racer = lambda: racers_lookup[derby_standings[racer_index]['car_number']] if len(derby_standings) > racer_index else None
            lineup = []  # result variable

            for heat in range(1, self.heats_per_round + 1):
                byes_in_heat = len([b for b in byes if b.bye.heat_number == heat])
                used_lanes = self.lanes_enabled - byes_in_heat
                starting_lane = (((self.current_round - 1) % used_lanes) + 1)

                for lane in range(1, self.lanes_enabled + 1):
                    offset_lane = (((lane + starting_lane) - 1) % used_lanes) + 1
                    if next_bye() is not None and next_bye().bye.lane_number == lane and next_bye().bye.heat_number == heat:
                        # Handle byes
                        lineup.append({
                            'lineup_detail': None,
                            'race_result': RaceResult(race_num, round_num, heat, lane, next_bye())
                        })
                        bye_index += 1
                    else:
                        # Handle regular racers
                        lineup.append({
                            'lineup_detail': derby_standings[racer_index],
                            'race_result': RaceResult(race_num, round_num, heat, offset_lane, next_racer())
                        })
                        racer_index += 1
                race_num += 1

            # ensure we didn't make a mistake
            if racer_index != len(non_bye_racers) or bye_index != len(byes)\
               or len(lineup) != self.heats_per_round * self.lanes_enabled:
                raise FozrException("Problem generating lineup for round. Check heats per round and enabled lanes")

            # add to database
            for record in lineup:
                uow.fozr_repository.add(record['race_result'])

            uow.commit()

    def rerun_prior_race(self):
        if self.current_race <= 1:
            raise FozrException("There is no prior race to run")

        with self._new_uow() as uow:
            dd = uow.derby_detail_repository.get_only_derby_detail()
            cur_raceid = RaceIdentifier(dd.race_number, dd.heats_per_round)
            prior_raceid = RaceIdentifier(dd.race_number - 1, dd.heats_per_round)
            dd.race_number -= 1

            if cur_raceid.round_number != prior_raceid.round_number:
                # we went back a round, which means we will need to resort for
                # the next round after the results of this final heat
                rr = uow.race_result_repository.get_race_results_by_round_number(cur_raceid.round_number)
                for r in rr:
                    uow.race_result_repository.delete(r)

            rr = uow.race_result_repository.get_race_results_by_race_number(prior_raceid.race_number)
            for r in rr:
                #print(r.race_result_id)
                r.time = None
                r.place = None
                r.timer_data = None
            uow.commit()

        self.load()

    def get_derby_standings(self):
        with self._new_uow() as uow:
            return uow.fozr_repository.get_derby_standings()


class RaceIdentifier:
    """
    Represents race number
    """
    def __init__(self, race_number, total_heats_per_round):
        self.total_heats_per_round = total_heats_per_round
        self.race_number = race_number

    def add(self):
        self.race_number += 1

    @property
    def round_number(self):
        return ((self.race_number - 1) // self.total_heats_per_round) + 1

    @property
    def heat_number(self):
        return ((self.race_number - 1) % self.total_heats_per_round) + 1

    def __repr__(self):
        return "Race #{0}: Round {1}, Heat {2}".format(self.race_number, self.round_number, self.heat_number)


class Timer:
    """
    Represents behaviors needed for the racing timer
    """
    def __init__(self):
        pass

    def parse_timer_data(self, raw_timer_data):
        """
        Takes raw timer data and converts it to a TimerData object
        """
        pat = r"(\d)\s+(\d+\.\d+)"
        place = 1
        timer_data = TimerData()
        timer_data.is_deleted = False
        timer_data.created_at = utils.datetime.now()
        util = FozrFactory().create_derby_util()
        for match in re.findall(pat, raw_timer_data):
            verbiage = util.get_place_verbiage(place, nth_format=False)
            lane = int(match[0])
            time = Decimal(match[1])
            setattr(timer_data, verbiage + '_place_lane', lane)
            setattr(timer_data, verbiage + '_place_time', time)
            place += 1
        return timer_data

    def log_timer_data(self, raw_timer_data):
        timer_data = self.parse_timer_data(raw_timer_data)

        # write to timer log file
        timestamp = timer_data.created_at
        with open(Config.settings['TIMER_LOG_FILEPATH'], "a") as timer_file:
            timer_file.write("{0}\t|\t".format(timestamp))
            timer_file.write("{0}\n".format(raw_timer_data.strip()))
            timer_file.close()

        # write to repository
        return timer_data


class LaneResult:
    lane = None
    time = None
    place = None

    def __init__(self, lane, time, place):
        self.lane = lane
        self.time = time
        self.place = place




#     def get_last_results(self):
#         results = self.get_race_lineup(self.get_race_num() - 1)
#         results = asquery(results).order_by(lambda x: x.place)
#         return results

#     def get_heats_per_round(self):
#         session = self.get_session()
#         derby = self.get_derby()
#         racers = session.query(Racer.car_num).count()
#         heats_per_round = racers // derby.lanes_enabled
#         if heats_per_round * derby.lanes_enabled != racers:
#             raise FozrException("Unexpected racer counts and heat lineup: " +
#                                 "racers={0}, heats={2}, lanes enabled={3}"\
#                                 .format(racers, heats_per_round, derby.lanes_enabled))
#         return heats_per_round
