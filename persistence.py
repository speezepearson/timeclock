"""
Defines data structures for long-term storage of timeclock data.

Those are:
- StateChange: a record of switching to state <state> at <time>.
   The log file is just a sequence of these.
- Period: represents a period of time spent on a state.
   It may be more natural to work with than StateChanges.
- Database: handles a log file, letting client code add new lines to
   it and iterate through past activity.
"""

import datetime
import re

TIME_FORMAT = "%Y.%m.%d %H:%M:%S"
TIME_PATTERN = r"\d\d\d\d.\d\d.\d\d \d\d:\d\d:\d\d"
STATE_PATTERN = r"[-a-zA-Z0-9_ ()]+"

class StateChange(object):
  """A timestamped record of switching to a given state.

  The log file is just a sequence of StateChanges. So, although it
  might seem natural to record *two* states, the one being switched
  from and the one being switched to, that would introduce
  (undesirable) redundancy, and so we don't.
  """
  # The format we use for StateChange => str conversion:
  FORMAT = "{time}: {state}"
  # And the regexp we use for str => StateChange:
  PATTERN = FORMAT.format(time="(?P<time>"+TIME_PATTERN+")",
                          state="(?P<state>"+STATE_PATTERN+")")

  def __init__(self, time, state):
    if re.match(STATE_PATTERN+"$", state) is None:
      raise ValueError("state must match regex "+STATE_PATTERN)
    self.time = time
    self.state = state

  def __eq__(self, other):
    return self.time == other.time and self.state == other.state
  def __str__(self):
    return self.FORMAT.format(time=self.time.strftime(TIME_FORMAT),
                              state=self.state)

  @classmethod
  def from_string(cls, s):
    """Converts a string into a StateChange.

    Is the left-inverse of __str__, i.e.
    >>> pc = StateChange(datetime.datetime.now(), "whatever")
    >>> assert StateChange.from_string(str(pc)) == pc
    will work.
    """
    match = re.match(cls.PATTERN, s)
    if match is None:
      raise ValueError("invalid state change string")
    time = datetime.datetime.strptime(match.group("time"), TIME_FORMAT)
    return StateChange(time=time, state=match.group("state"))

class Period(object):
  """A period of time spent on some state."""
  def __init__(self, state, start, stop):
    self.state = state
    self.start = start
    self.stop = stop

  def __str__(self):
    return "{state}: {start} => {stop}".format(
             state=self.state,
             start=self.start,
             stop=self.stop)

  @property
  def duration(self):
    return self.stop - self.start


class Database(object):
  """Handles the file in which we maintain our records."""

  def __init__(self, file):
    self.file = file

  def write_change(self, state, time=None, repeat=False):
    """Appends a new line describing a change to the log file.

    Arguments:
    - state: string
    - time: datetime.datetime instance (default: set to now())
    - repeat: if false (default), if self.last_state() is the
      same as the given state, do nothing.
    """
    if (not repeat) and self.last_state() == state:
      return

    if time is None:
      time = datetime.datetime.now()

    change = StateChange(time=time, state=state)
    self.file.seek(0, 2) # Seek to end of file to append
    self.file.write(str(change) + "\n")
    self.file.flush() # Make sure it's written, in case of crash

  def iter_changes(self):
    """Iterates through the state changes in the file."""
    self.file.seek(0, 0)
    for line in self.file:
      yield StateChange.from_string(line[:-1])

  def iter_periods(self):
    """Iterates through the periods between the state changes in the file."""
    changes = self.iter_changes()
    try:
      prev_change = changes.next()
    except StopIteration:
      return

    for next_change in changes:
      yield Period(prev_change.state, prev_change.time, next_change.time)
      prev_change = next_change

  def states(self):
    """Returns the set of all states encountered in the database."""
    return set(change.state for change in self.iter_changes())

  def last_state(self):
    """Returns the last recorded state in the database."""
    result = None
    for c in self.iter_changes():
      result = c
    return None if result is None else result.state
