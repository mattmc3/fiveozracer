"""
Represents a set of stand-alone utility functions for FozR.
Note, these do not have database or model dependencies
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

import math
import re
from decimal import Decimal
from collections import OrderedDict
from asq.initiators import query as asquery
from exceptions import FozrException
from collections import namedtuple


class DerbyUtil:
    """
    Represents a set of simple utility functions for a Derby
    """

    def __init__(self):
        pass

    def get_race_round_details(self, racers, lanes_enabled):
        """
        Creates a description of a round
        returns:
            a list of dicts like so (lanes_enabled == 5):
            [{'group': 'scouts', 'num_racers': 10, 'num_byes': 0, 'starting_heat': 1, 'heats_per_round': 2},
            {'group': 'siblings', 'num_racers': 4, 'num_byes': 1, 'starting_heat': 3, 'heats_per_round': 1}]
        """
        groupings = self.group_racers_by_racing_class(racers)
        result = []
        starting_heat = 1
        for (group, racer_list) in groupings.items():
            num_racers = len(racer_list)
            num_byes = (math.ceil(num_racers / lanes_enabled) * lanes_enabled) - num_racers
            heats_per_round = (num_racers + num_byes) // lanes_enabled
            result.append({
                'group': group,
                'num_racers': num_racers,
                'racers': racer_list,
                'num_byes': num_byes,
                'starting_heat': starting_heat,
                'heats_per_round': heats_per_round
            })
            starting_heat += heats_per_round

        return result

    def group_racers_by_racing_class(self, racers):
        qry = asquery(racers) \
            .order_by(lambda x: x.racing_class.racing_class_id) \
            .then_by(lambda x: None if x.grade is None else x.grade.grade_id) \
            .then_by(lambda x: x.car_number) \
            .group_by(lambda x: x.racing_class.name)
        result = OrderedDict()
        for g in qry:
            result[g.key] = list(g)
        return result

    def get_place_verbiage(self, place, nth_format=True):
        if place == 1:
            return "1st" if nth_format else "first"
        elif place == 2:
            return "2nd" if nth_format else "second"
        elif place == 3:
            return "3rd" if nth_format else "third"
        elif place == 4:
            return "4th" if nth_format else "fourth"
        elif place == 5:
            return "5th" if nth_format else "fifth"
        elif place == 6:
            return "6th" if nth_format else "sixth"
        elif place == 7:
            return "7th" if nth_format else "seventh"
        elif place == 8:
            return "8th" if nth_format else "eighth"
        else:
            return "0" if nth_format else "none"

    def get_lookup(self, object_list, key_selector):
        result = OrderedDict()
        for obj in object_list:
            key = key_selector(obj)
            result[key] = obj
        return result

    def escape_sql_like_pattern(self, pattern):
        if pattern is None:
            raise ValueError('pattern cannot be None')
        return re.sub(r"([\[_%])", r"[\g<1>]", str(pattern))
