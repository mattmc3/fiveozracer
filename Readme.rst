Five oz Racer
*************

Pinewood Derby Software for Pack 814, Columbus OH


Technology
----------
This software is written in Python using the Flask web framework and
SQLAlchemy ORM.


RST Files
---------
http://docutils.sourceforge.net/docs/user/rst/quickstart.html


Installation Notes
------------------
Python packages installed using `pip` utility.
pip install -r requirements.txt
  + pip install flask
  + pip install sqlalchemy
  + pip install asq


Serial to USB Driver
--------------------
http://www.prolific.com.tw/US/ShowProduct.aspx?p_id=229&pcid=41


Database syncing
----------------
You can run the following command to apply ORM models to the
database and start fresh: `python models.py`.  Currently there
is no migrations support.


Timer
-----
The TimerReader.py file that must be manually run from the command
line with the timer connected during a race.  This script handles the
serial connectivity and reads from the timer.



Links
-----
# http://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
# https://github.com/github/gitignore/blob/master/Python.gitignore
# http://stackoverflow.com/questions/4142151/python-how-to-import-the-class-within-the-same-directory-or-sub-directory


Setup Notes:
------------
# Remember to turn on lights.  An always green 'active' light on the timer
means that the lights aren't on.
# Remember to flip the lane switches to match the lanes enabled
# Cmd shift F - Chrome full screen

TODO:
Sizing of screen
random lane sort
delete time practice
ensure timer run data lanes recorded matches lanes enabled variable

DNF for fast cars stick in first heat indefinitely
0.000 don't register
Supplies: Sharpies
Sort for round vs sort for results


Pack 128 learnings:
Fix multiple byes per heat
Fix dupe sorts per round
Add screen for lane assignment viewing
Add screen for race re-running
Decimal vs Float



data_structure
Derby:
	lanes_enabled
	name
	derby_date
	contact
	racing_groups: [
		name
		racers: [
			Racer:
				car_number
				driver_name
				grade
				racing_class
				Bye:
					lane_assignment
					heat_assignment
		]
	]
	lineup [
		Lineup:
			rounds
				heats
					racer
					lane
					time
					place
	]

Quit trying to get rid of the grades and racing_classes lookup tables.  It won't
work.  You need ordinals for those.

Structure
---------
Timer
	.is_ready
	.read_next()

Derby
	*** Properties
	.name
	.derby_date
	.notes

	*** Behaviors
	.load()
	.prepare_timer()
	.prepare_racers()
	.prepare_races()

	.start_races()
	.stop_races()

	.run_next_race()
	.rerun_prior_race()

	._sort_for_round()
	.get_round_lineup(round_number)

	.get_current_race()
	.get_current_round()
	.get_current_heat()
	.get_last_race_result()
	.get_currently_racing()
	.get_on_deck()
	.get_racers()
	.get_derby_results()
	.get_heats_per_round()
	.get_lanes_enabled()
	.get_heats_per_round()


DerbyStandings
	.get_overall_standings()
	.get_standings_by_den()
	.get_standings_by_grade()

TimerResult
	.lane_results

LaneResult
	.lane
	.place
	.rank

RaceResult
	.race_number
	.racer
	.timer_result

RoundSorter

Racer

Grade

RacingClass

FozrRepository
