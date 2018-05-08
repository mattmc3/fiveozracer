import os
import inspect


def get_base_path():
    script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    result = os.path.abspath(script_path)
    return result

def get_settings(db_folder="db"):
    db_name = "fozr.sqlite"

    base_path = get_base_path()
    data_path = os.path.join(base_path, "db")

    settings = {
        'DATABASE_PATH': os.path.join(data_path, db_name),
        'DATABASE_URI': 'sqlite:///' + os.path.join(data_path, db_name),
        'DATA_PATH': data_path,
        'SQL_PATH': os.path.join(base_path, "sql"),
        'LOGGING_ON': False,
        'DNF_TIME': '6.0000',
        'INIT_DATA_PATH': os.path.join(data_path, "init"),
        'DERBIES_DATA': "derbies.csv",
        'GRADES_DATA': "grades.csv",
        'RACING_CLASSES_DATA': "racing_classes.csv",
        'RACERS_DATA': "racers.csv",
        'STRING_TRANSLATIONS_DATA': "string_translations.csv",
        'TIMER_LOG_FILEPATH': os.path.join(data_path, "TimerLog.txt"),
    }
    return settings


class Config:
    settings = None
Config.settings = get_settings()
