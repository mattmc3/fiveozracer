"""
Defines object factories
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

from config import Config
from data_access import DataUtil
from fozr_utils import DerbyUtil
from db_repositories import UnitOfWork


class FozrFactory:
    def __init__(self):
        self.settings = Config.settings

    def create_data_util(self):
        return DataUtil()

    def create_derby_util(self):
        return DerbyUtil()

    def create_unit_of_work(self):
        return UnitOfWork()
