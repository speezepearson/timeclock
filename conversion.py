"""
Converts the old timeclock file format into the new one.

usage: python conversion.py source_file dest_file

Sample translation:
 On 1970.01.01, someone works on alpha from 12:00 until 14:00,
 then works on beta until 17:00,
 then goes idle until 18:00,
 then works on alpha until 19:00,
 then goes idle until 20:00,
 then works on gamma until 21:00. (Then becomes idle.)
Old file:
   alpha 1970.01.01 12:00:00 on
   alpha 1970.01.01 14:00:00 off: 2.0 hours
   beta 1970.01.01 14:00:00 on
   beta 1970.01.01 17:00:00 off: 3.0 hours
   alpha 1970.01.01 18:00:00 on
   alpha 1970.01.01 19:00:00 off: 1.0 hours
   gamma 1970.01.01 20:00:00 on
   gamma 1970.01.01 21:00:00 off: 1.0 hours
New file:
   1970.01.01 12:00:00: alpha
   1970.01.01 14:00:00: beta
   1970.01.01 17:00:00: Idle
   1970.01.01 18:00:00: alpha
   1970.01.01 19:00:00: Idle
   1970.01.01 20:00:00: gamma
   1970.01.01 21:00:00: Idle
"""

import re
import datetime
from timeclock.persistence import Database
from timeclock import IDLE

# The old file is accurate to (1/1000) hours, a few seconds.
# We'll want to define a threshold for a "significant" time difference,
#  given that:
DT_THRESHOLD = timeclock.timedelta(seconds=5)

# How the old file format stored information:
OLD_TIME_FORMAT = "%Y.%m.%d %H:%M:%S"
OLD_OFF_RECORD_FORMAT = r"(?P<state>[^ ]*) (?P<stop>[\d.]{10} [\d:]{8}) off: (?P<hours>[\d.]+) hours"

def convert(from_file, to_file):
  """Convert data from an old-formatted file to a new one."""
  # With the old setup, the meat of the log file was the "off records",
  # which said "I've been working on <this state> for <this long>."
  # We just take each of those (ignoring other lines), calculate the
  # start time, and write a state change with that time and state
  # to the new database.
  db = Database(to_file)
  last_stop = None
  for line in from_file:
    m = re.match(OLD_OFF_RECORD_FORMAT, line.strip())
    if m is None:
      continue
    state = m.group("state")
    stop = datetime.datetime.strptime(m.group("stop"), OLD_TIME_FORMAT)
    hours = float(m.group("hours"))
    start = stop - datetime.timedelta(hours=hours)

    # If there's a gap between off records, we were idle.
    if ((last_stop is not None) and
        abs(start-last_stop) > DT_THRESHOLD):
      db.write_change(time=last_stop, state=IDLE)
    db.write_change(time=start, state=state)

    last_stop = stop

  db.write_change(time=last_stop, state=IDLE)

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description="update timeclock file formats")
  parser.add_argument("-g", "--goal", help="file to assert equivalence to")
  parser.add_argument("source", help="old-style file to convert")
  parser.add_argument("dest", help="file to write new version to")

  args = parser.parse_args()
  with open(args.source) as src, open(args.dest, "w+") as dst:
    convert(src, dst)

  if args.goal is not None:
    with open(args.goal) as goal, open(args.dest) as out:
      goal_changes = Database(goal).iter_changes()
      out_changes = Database(out).iter_changes()
      for (c1, c2) in itertools.izip(goal_changes, out_changes):
        assert c1.state == c2.state
        assert abs(c1.time - c2.time) < DT_THRESHOLD