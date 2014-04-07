"""
Keep track of time spent on various projects.

This package provides tools for logging timestamped changes to
something's state, written with the purpose in mind of a timeclock.

Run as a script, this package is a commmand-line timeclock utility.
It puts up a small window with a radio button for each of various
projects listed on the command line. When you start working on one
of the listed projects, you click on its radio button to "start the
clock" for that project. Clicking on any other button stops the
clock for that project, resulting in a line being written to the log
file.

If multiple copies of this program are run at the same time,
the contents of the log file are not guaranteed to make sense.
"""

IDLE = "Idle"

from . import gui
from . import persistence
from . import reports
from .parser import parser # parser is the only thing of use in that file.