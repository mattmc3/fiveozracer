"""
Common utility helpers, not specific to project
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

import datetime
import time


class StringUtils:
    def is_none_or_empty(self, string):
        return string is None or len(str(string)) == 0

    def is_none_or_whitespace(self, string):
        return string is None or len(str(string).strip()) == 0


class DateTimeUtils:
    _fn_get_now = None

    def __init__(self):
        self.set_now_function(self._sys_now)

    def set_now_function(self, fn_get_now):
        self._fn_get_now = fn_get_now

    def now(self):
        return self._fn_get_now()

    def _sys_now(self):
        return datetime.datetime.fromtimestamp(time.time())


class Utils:
    string = StringUtils()
    datetime = DateTimeUtils()
