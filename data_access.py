"""
Defines FozR SQLAlchemy database models and data access layer
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

import csv
import re
import inspect
import logging
import sqlite3
import dateutil.parser as dateparser
import datetime
import os
from decimal import Decimal
from exceptions import FozrException
from sqlalchemy import create_engine
from sqlalchemy import types, Column, ForeignKey, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from collections import namedtuple
from fozr_utils import DerbyUtil
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from config import Config


class SqliteNumeric(types.TypeDecorator):
    """
    SQLite does not handle DECIMAL fields correctly, and precision
    is lost in a float conversion. This class handles the conversion
    of decimal data to a VARCHAR storage in SQLite and back again.
    """
    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Decimal(value)

Numeric = SqliteNumeric
Base = declarative_base()


#region SQLAlchemy mapped classes


class TimerData(Base):
    """
    Represents a single timing read from the timer
    """
    __tablename__ = 'timer_data'
    timer_data_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
    first_place_time = Column(Numeric(6, 4))
    first_place_lane = Column(Integer)
    second_place_time = Column(Numeric(6, 4))
    second_place_lane = Column(Integer)
    third_place_time = Column(Numeric(6, 4))
    third_place_lane = Column(Integer)
    fourth_place_time = Column(Numeric(6, 4))
    fourth_place_lane = Column(Integer)
    fifth_place_time = Column(Numeric(6, 4))
    fifth_place_lane = Column(Integer)
    sixth_place_time = Column(Numeric(6, 4))
    sixth_place_lane = Column(Integer)
    seventh_place_time = Column(Numeric(6, 4))
    seventh_place_lane = Column(Integer)
    eighth_place_time = Column(Numeric(6, 4))
    eighth_place_lane = Column(Integer)

    @property
    def lane_results(self):
        result = [
            LaneResult(self.first_place_lane, self.first_place_time, 1),
            LaneResult(self.second_place_lane, self.second_place_time, 2),
            LaneResult(self.third_place_lane, self.third_place_time, 3),
            LaneResult(self.fourth_place_lane, self.fourth_place_time, 4),
            LaneResult(self.fifth_place_lane, self.fifth_place_time, 5),
            LaneResult(self.sixth_place_lane, self.sixth_place_time, 6),
            LaneResult(self.seventh_place_lane, self.seventh_place_time, 7),
            LaneResult(self.eighth_place_lane, self.eighth_place_time, 8)
        ]
        return [x for x in result if x.time is not None]

    def __repr__(self):
        return "  ".join(["{0} {1}".format(x.lane, x.time) for x in self.lane_results])


class DerbyDetail(Base):
    """
    Represents the information for a derby
    """
    __tablename__ = 'derby_details'
    derby_detail_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255))
    derby_date = Column(DateTime)
    notes = Column(Text)
    lanes_enabled = Column(Integer)
    heats_per_round = Column(Integer)
    race_number = Column(Integer)

    def __init__(self, derby_detail_id, name, notes, derby_date, lanes_enabled, heats_per_round=0, race_number=1):
        self.derby_detail_id = derby_detail_id
        self.name = name
        self.notes = notes
        self.derby_date = derby_date
        self.lanes_enabled = lanes_enabled
        self.heats_per_round = heats_per_round
        self.race_number = race_number

    def __repr__(self):
        return self.name


class RacingClass(Base):
    """
    Represents a competition class for racers. Racers only compete
    with other racers in their class.
    """
    __tablename__ = 'racing_classes'
    racing_class_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255))

    def __init__(self, racing_class_id, name):
        self.racing_class_id = racing_class_id
        self.name = name

    def __repr__(self):
        return self.name


class Grade(Base):
    """
    Represents the grade or rank a scout has achieved.
    """
    __tablename__ = 'grades'
    grade_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255))

    def __init__(self, grade_id, name):
        self.grade_id = grade_id
        self.name = name

    def __repr__(self):
        return self.name


class Bye(Base):
    """
    Represents a bye, which is a placeholder for a racer when
    the total number of racers is not divisible by the number of
    lanes being run
    """
    __tablename__ = 'byes'
    bye_number = Column(Integer, primary_key=True, autoincrement=False)
    heat_number = Column(Integer)
    lane_number = Column(Integer)

    def __init__(self, bye_number, heat_number, lane_number):
        self.bye_number = bye_number
        self.heat_number = heat_number
        self.lane_number = lane_number


class Racer(Base):
    """
    Represents a racer and their derby car
    """
    __tablename__ = 'racers'
    car_number = Column(Integer, primary_key=True, autoincrement=False)
    driver_name = Column(String(255))
    grade_id = Column(Integer, ForeignKey('grades.grade_id'))
    grade = relationship(Grade)
    racing_class_id = Column(Integer, ForeignKey('racing_classes.racing_class_id'))
    racing_class = relationship(RacingClass)
    den = Column(Integer)
    bye_number = Column(Integer, ForeignKey('byes.bye_number'))
    bye = relationship(Bye)
    weight = Column(Numeric(4, 2))

    def __init__(self, car_number, driver_name, racing_class, grade=None, den=None, bye=None, weight=None):
        self.car_number = car_number
        self.driver_name = driver_name
        self.racing_class = racing_class
        self.grade = grade
        self.den = den
        self.bye = bye
        self.weight = weight

    @property
    def car_id(self):
        return "{0:02d} - {1}".format(self.car_number, self.driver_name)

    def __repr__(self):
        return self.car_id


class RaceResult(Base):
    """
    Represents the actual results of each race for each racer on their
    assigned lane
    """
    __tablename__ = 'race_results'
    race_result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_number = Column(Integer)
    round_number = Column(Integer)
    heat_number = Column(Integer)
    lane_number = Column(Integer)
    car_number = Column(Integer, ForeignKey('racers.car_number'))
    racer = relationship(Racer)
    time = Column(Numeric(6, 4))
    place = Column(Integer)
    timer_data_id = Column(Integer, ForeignKey('timer_data.timer_data_id'))
    timer_data = relationship(TimerData)

    def __init__(self, race_number, round_number, heat_number, lane_number, racer, time=None, place=None):
        self.race_number = race_number
        self.round_number = round_number
        self.heat_number = heat_number
        self.lane_number = lane_number
        self.racer = racer
        self.time = time
        self.place = place

    def __repr__(self):
        util = DerbyUtil()
        text = "{0:02d}: (r{1},h{2},l{3}) {4}".format(self.race_number, self.round_number, self.heat_number,
                                                      self.lane_number, self.racer)
        if self.time is not None:
            text += " {0} place @{1:.4f}".format(util.get_place_verbiage(self.place), self.time)
        return text


class StringTranslation(Base):
    __tablename__ = 'string_translations'
    __table_args__ = {'sqlite_autoincrement': True}
    string_translation_id = Column(Integer, primary_key=True, autoincrement=True)
    context = Column(String(255))
    pattern = Column(String(1000))
    translation = Column(String(255))

    def __init__(self, context, pattern, translation):
        self.context = context
        self.pattern = pattern
        self.translation = translation

#endregion


def dict_factory(cursor, row):
    """
    Helper for direct sqlite queries to convert row to dict
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Note: Has to be co-located with db models in order for init_db to work
class DataUtil:

    def init_db(self):
        """
        Creates schema and loads any initialization data into the database
        """
        logger = logging.getLogger('fozr.db_models')
        logger.setLevel(logging.INFO)

        # Create an engine that stores data
        engine = create_engine(Config.settings['DATABASE_URI'])

        # Create all tables in the engine. This is equivalent to "Create Table"
        # statements in raw SQL.
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        date_converter = lambda x: dateparser.parse(x)
        int_converter = lambda x: int(x) if x.isdigit() else None

        with self.session_scope() as session:
            # load data
            derby_data = self.get_data_from_file(
                self.get_data_file_path('DERBIES_DATA'),
                field_converters={'derby_date': date_converter,
                                  'lanes_enabled': int_converter,
                                  'heats_per_round': int_converter})
            self.load_table(session, DerbyDetail, derby_data)

            grade_data = self.get_data_from_file(
                self.get_data_file_path('GRADES_DATA'),
                field_converters={'grade_id': int_converter})
            self.load_table(session, Grade, grade_data)

            racing_class_data = self.get_data_from_file(
                self.get_data_file_path('RACING_CLASSES_DATA'),
                field_converters={'racing_class_id': int_converter})
            self.load_table(session, RacingClass, racing_class_data)

            string_translations_data = self.get_data_from_file(self.get_data_file_path('STRING_TRANSLATIONS_DATA'))
            self.load_table(session, StringTranslation, string_translations_data)

        logger.info("Data Init Complete")

    @contextmanager
    def session_scope(self):
        """Begin a transactional scope around a series of db operations."""
        session = self.get_new_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_new_session(self):
        """
        Returns a SQLAlchemy session
        """

        engine = create_engine(Config.settings['DATABASE_URI'])
        # Bind the engine to the metadata of the Base class so that the
        # declaratives can be accessed through a DBSession instance
        Base.metadata.bind = engine

        DBSession = sessionmaker(bind=engine)
        # A DBSession() instance establishes all conversations with the database
        # and represents a "staging zone" for all the objects loaded into the
        # database session object. Any change made against the objects in the
        # session won't be persisted into the database until you call
        # session.commit(). If you're not happy about the changes, you can
        # revert all of them back to the last commit by calling
        # session.rollback()
        session = DBSession()
        return session

    def get_data_file_path(self, config_name):
        init_dir = Config.settings['INIT_DATA_PATH']
        return os.path.join(init_dir, Config.settings[config_name])


    def get_data_from_file(self, filepath, delimiter=",", field_converters=None):
        """
        Returns a list of dictionaries from parsing a delimited
        flat file
        """
        field_converters = field_converters if field_converters is not None else {}
        header = True
        field_names = []
        data = []
        for row in csv.reader(open(filepath), delimiter=delimiter):
            if header:
                header = False
                field_names = row
            elif len(row) > 0:
                d = dict(zip(field_names, row))
                for (key, converter) in field_converters.items():
                    if key in d:
                        d[key] = converter(d[key])
                data.append(d)

        return data

    def load_table(self, session, cls, data):
        for d in data:
            # remove keys that are not part of the argument list for __init__
            arg_names = [x for x in inspect.getargspec(cls.__init__).args if x != 'self']
            args = {}
            for (key, value) in d.items():
                if key in arg_names:
                    args[key] = value

            fozr_obj = cls(**args)
            session.add(fozr_obj)

    def execute_sql_file(self, sql_filename, params=(), use_default_sql_location=True):
        sql_filepath = sql_filename if not use_default_sql_location else self.get_sql_path(sql_filename)
        sql = open(sql_filepath).read()
        with sqlite3.connect(Config.settings['DATABASE_PATH']) as conn:
            conn.row_factory = dict_factory
            cur = conn.cursor()
            cur.execute(sql, params)
            results = cur.fetchall()
        return results

    def get_sql_path(self, sql_filename):
        sql_filepath = os.path.join(Config.settings['SQL_PATH'], sql_filename)
        return sql_filepath


class StringTranslator:
    def __init__(self, context, translations):
        self.context = context
        self.translations = translations

    def translate(self, string, raise_if_translation_fails=False):
        if string is not None:
            for st in self.translations:
                if re.match(st.pattern, string):
                    return st.translation
        if not raise_if_translation_fails:
            return None
        else:
            raise FozrException("No translation for {0} value: {1}".format(self.context, string))


class LaneResult:
    lane = None
    time = None
    place = None

    def __init__(self, lane, time, place):
        self.lane = lane
        self.time = time
        self.place = place
