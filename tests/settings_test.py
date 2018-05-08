import os
import inspect

db_name = "fozr_test.sqlite"


def get_full_path(rel_path):
    script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    result = os.path.abspath(os.path.join(script_path, "../" + rel_path))
    return result

settings_test = {
    'DATABASE_PATH': os.path.join(get_full_path("data"), db_name),
    'DATABASE_URI': 'sqlite:///' + os.path.join(get_full_path("data"), db_name),
    'DATA_PATH': get_full_path("data"),
    'LOGGING_ON': False,
    'DNF_TIME': '6.0000',
    'INIT_DATA_PATH': get_full_path("data/init_test"),
    'DERBIES_DATA': get_full_path("data/init_test/derbies.csv"),
    'GRADES_DATA': get_full_path("data/init/grades.csv"),
    'RACING_CLASSES_DATA': get_full_path("data/init/racing_classes.csv"),
    'RACERS_DATA': get_full_path("data/init_test/racers.csv"),
    'STRING_TRANSLATIONS_DATA': get_full_path("data/init/string_translations.csv"),
    'TIMER_LOG_FILEPATH': get_full_path("data/TEST_TimerLog.txt"),
}
