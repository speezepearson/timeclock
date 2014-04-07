"Defines the command-line argument parser for the timeclock program."

import os
import argparse

description = "Record time spent on projects or report past times."
usage = """timeclock [-f FILE] [-t SECONDS] [-q] PROJECT ... # record work
       timeclock [-f FILE] -R PROJECT ... # print a report and exit"""

DEFAULT_LOGFILE_NAME = os.path.join(os.environ["HOME"], "timeclock.dat")

parser = argparse.ArgumentParser(description=description, usage=usage)
parser.add_argument("-f", "--file", default=DEFAULT_LOGFILE_NAME,
                    help="path of the logfile (default $HOME/timeclock.dat)")
parser.add_argument("-R", "--report", action="store_true", dest="reporting",
                    help="report of all work on given projects, not record new")
parser.add_argument("-t", "--remind-time", type=int, default=120,
                    help="remind every N seconds (default 120)")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="don't beep when reminding")
parser.add_argument("projects", metavar="PROJECT", nargs="+",
                    help="projects to report on")
