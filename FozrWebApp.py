from flask import Flask
from flask import render_template

from factories import FozrFactory
from FiveOzRacer import Derby
from collections import namedtuple
from config import Config
from pprint import pprint

__author__ = 'Matt McElheny'
__email__ = "mattmc3@gmail.com"

app = Flask(__name__)
#app.config.update(
#    DEBUG=True,
#    SEND_FILE_MAX_AGE_DEFAULT=1
#)
#app.config['SQLALCHEMY_DATABASE_URI'] = settings['DATABASE_URI']
#db = SQLAlchemy(app)

factory = FozrFactory()


def get_uow():
    return factory.create_unit_of_work().begin()


def get_derby():
    result = Derby()
    result.load()
    return result


@app.route('/')
def index():
    return display()

@app.route('/display')
def display():
    derby = get_derby()
    context = {
        'race_results': derby.get_last_race_result(),
        'currently_racing': derby.get_currently_racing(),
        'on_deck': derby.get_on_deck(),
        'race_info': derby.race_identifier
    }
    return render_template('display.html', context=context)

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route('/partials/last-results')
def partials_last_results():
    derby = get_derby()
    results = derby.get_last_race_result(),
    return render_template('partials/last_results.html', race_results=results)

# @app.route('save_timer_data', methods=['POST'])
# def save_timer_data():
#     raw_timer_data = int(request.form['timerData'])
#     util = DerbyUtil()
#     td = util.get_timer_data(raw_timer_data)
#     db.session.add(td)
#     db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
