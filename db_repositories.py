"""
Defines FozR SQLAlchemy database models and data access layer
"""

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, joinedload, make_transient
from sqlalchemy.ext.declarative import declarative_base
from data_access import Bye, DerbyDetail, Grade, RaceResult, Racer, RacingClass, StringTranslation,\
    TimerData, StringTranslator, DataUtil
from contextlib import contextmanager
from config import Config
from common import Utils
from collections import namedtuple

Base = declarative_base()


class UnitOfWork:
    def __init__(self):
        self._fozr_repo = None
        self._session = self._get_new_session()
        # repo variable for each table's repo
        self._bye_repo = None
        self._derby_detail_repo = None
        self._grade_repo = None
        self._race_result_repo = None
        self._racer_repo = None
        self._racing_class_repo = None
        self._string_translation_repo = None
        self._timer_data_repo = None

    @contextmanager
    def begin(self):
        """Begin a transactional scope around a series of db operations."""
        try:
            yield self
            self._session.commit()
        except:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    def _get_new_session(self):
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

    @property
    def fozr_repository(self):
        if self._fozr_repo is None:
            self._fozr_repo = FozrRepository(self._session)
        return self._fozr_repo

    @property
    def bye_repository(self):
        if self._bye_repo is None:
            self._bye_repo = ByeRepository(self, self._session)
        return self._bye_repo

    @property
    def derby_detail_repository(self):
        if self._derby_detail_repo is None:
            self._derby_detail_repo = DerbyDetailRepository(self, self._session)
        return self._derby_detail_repo

    @property
    def grade_repository(self):
        if self._grade_repo is None:
            self._grade_repo = GradeRepository(self, self._session)
        return self._grade_repo

    @property
    def race_result_repository(self):
        if self._race_result_repo is None:
            self._race_result_repo = RaceResultRepository(self, self._session)
        return self._race_result_repo

    @property
    def racer_repository(self):
        if self._racer_repo is None:
            self._racer_repo = RacerRepository(self, self._session)
        return self._racer_repo

    @property
    def racing_class_repository(self):
        if self._racing_class_repo is None:
            self._racing_class_repo = RacingClassRepository(self, self._session)
        return self._racing_class_repo

    @property
    def string_translation_repository(self):
        if self._string_translation_repo is None:
            self._string_translation_repo = StringTranslationRepository(self, self._session)
        return self._string_translation_repo

    @property
    def timer_data_repository(self):
        if self._timer_data_repo is None:
            self._timer_data_repo = TimerDataRepository(self, self._session)
        return self._timer_data_repo

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()


class FozrRepository:
    def __init__(self, session):
        self._session = session

    def add(self, entity):
        self._session.add(entity)

    def query(self, klass):
        return self._session.query(klass)

    def delete(self):
        return self._session.delete()

    def get_derby_standings(self):
        du = DataUtil()
        result = du.execute_sql_file("get_derby_standings.sql")
        return result

    def get_race_results(self):
        du = DataUtil()
        result = du.execute_sql_file("get_race_results.sql")
        return result


class BaseRepository:
    def __init__(self, klass, unit_of_work, session):
        self._klass = klass
        self._unit_of_work = unit_of_work
        self._session = session

    def all(self):
        return self._session.query(self._klass).all()

    def find(self):
        return self._session.query(self._klass)

    def add(self, entity):
        return self._session.add(entity)

    def delete(self, entity):
        return self._session.delete(entity)

    def delete_all(self):
        return self._session.query(self._klass).delete()


class ByeRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(ByeRepository, self).__init__(Bye, unit_of_work, session)


class DerbyDetailRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(DerbyDetailRepository, self).__init__(DerbyDetail, unit_of_work, session)

    def get_only_derby_detail(self):
        return self._session.query(DerbyDetail).one()


class GradeRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(GradeRepository, self).__init__(Grade, unit_of_work, session)


class RaceResultRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(RaceResultRepository, self).__init__(RaceResult, unit_of_work, session)

    def get_race_results_by_race_number(self, race_number):
        results = self._session\
                      .query(RaceResult)\
                      .options(joinedload('racer'))\
                      .filter(RaceResult.race_number == race_number)\
                      .order_by(RaceResult.lane_number)\
                      .all()
        return results

    def get_race_results_by_round_number(self, round_number):
        results = self._session\
                      .query(RaceResult)\
                      .options(joinedload('racer'))\
                      .filter(RaceResult.round_number == round_number)\
                      .order_by(RaceResult.race_number)\
                      .order_by(RaceResult.lane_number)\
                      .all()
        return results

    def get_race_lineup(self, race_number):
        results = self.get_race_results_by_race_number(race_number)
        lanes_enabled = self._session.query(DerbyDetail).one().lanes_enabled

        if results is None or len(results) == 0:
            RaceResultFake = namedtuple('RaceResultFake', 'race_result_id racer lane_number time place')
            RacerFake = namedtuple('RacerFake', 'car_id')
            results = []
            for i in range(0, lanes_enabled):
                results.append(RaceResultFake(race_result_id=i, racer=RacerFake(car_id=''), lane_number=i+1, time=0, place=0))
        else:
            for r in results:
                make_transient(r)
                make_transient(r.racer)
        return results

    def get_max_lineup_round_number(self):
        result = self._session\
                     .query(func.max(RaceResult.round_number))
        return result

    def is_round_lineup_calculated(self, round_number):
        result = self._session\
                     .query(RaceResult)\
                     .filter(RaceResult.round_number == round_number)\
                     .first()
        return result is not None


class RacerRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(RacerRepository, self).__init__(Racer, unit_of_work, session)

    def reload_racers(self, racer_data):
        trans_repo = self._unit_of_work.string_translation_repository
        grade_trans = trans_repo.get_string_translator("grade")
        rc_trans = trans_repo.get_string_translator("racing_class")

        grades = self._session.query(Grade).all()
        dict_grades = {g.grade_id: g for g in grades}

        racing_classes = self._session.query(RacingClass).all()
        dict_racing_classes = {rc.racing_class_id: rc for rc in racing_classes}

        # add racers
        racers = []
        for r in racer_data:
            grade = None
            if not Utils().string.is_none_or_whitespace(r.get('grade')):
                if r['grade'].isdigit():
                    grade_id = int(r['grade'])
                else:
                    grade_id = int(grade_trans.translate(r.get('grade'), True))
                grade = dict_grades[grade_id]

            if r['racing_class'].isdigit():
                rc_id = int(r['racing_class'])
            else:
                rc_id = int(rc_trans.translate(r['racing_class'], True))

            rcr = Racer(r['car_number'], r['driver_name'], dict_racing_classes[rc_id], grade, r.get('den'))
            racers.append(rcr)

        # clear old records and load new ones
        self._session.query(Racer).delete()
        for r in racers:
            self._session.add(r)

    def get_bye_racers(self):
        byes = self._session.query(Racer)\
            .join(Racer.bye)\
            .order_by(Bye.heat_number)\
            .order_by(Bye.lane_number)\
            .all()
        return byes

    def get_non_bye_racers(self):
        racers = self._session.query(Racer)\
            .filter(Racer.bye == None)\
            .order_by(Racer.driver_name)\
            .all()
        return racers


class RacingClassRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(RacingClassRepository, self).__init__(RacingClass, unit_of_work, session)

    def get_by_name(self, name):
        return self._session.query(RacingClass).filter(RacingClass.name == name).one()


class StringTranslationRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(StringTranslationRepository, self).__init__(StringTranslation, unit_of_work, session)

    def get_string_translator(self, context):
        translations = self._session.query(StringTranslation)\
                                    .filter(StringTranslation.context == context)\
                                    .all()
        return StringTranslator(context, translations)


class TimerDataRepository(BaseRepository):
    def __init__(self, unit_of_work, session):
        super(TimerDataRepository, self).__init__(TimerData, unit_of_work, session)
