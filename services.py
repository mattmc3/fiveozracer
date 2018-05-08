"""
Defines DDD services
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

import os
from config import Config


class ResourceService:
    """
    Get resources
    """
    def __init__(self):
        self.settings = Config.settings

    def get_sql_resource(self, resource_name):
        sql_filepath = os.path.join(Config.settings['DATA_PATH'], 'sql', resource_name)
        sql = open(sql_filepath).read()
        return sql
