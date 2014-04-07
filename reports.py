"""
Produce bird's-eye views of all time spent in various states.
"""

import datetime

def daily_durations(periods):
  """Returns a dict: dates => summed durations of all periods on that date.

  i.e. for each date including any of the given periods, the resulting
  dict maps that date to the total duration of all periods starting on
  that date. (It won't work as you might expect if any period includes
  midnight, but that shouldn't happen often.)
  """
  result = {}
  for period in periods:
    date = period.start.date()
    if date not in result:
      result[date] = datetime.timedelta(0)
    result[date] += period.duration
  return result

def build_report_string(db, states):
  """Build a string summarizing time spent on the given states.

  The resulting string looks like:
    proj1 2013.06.18   0.0025   0.0025
    proj1 2013.06.19   0.0369   0.0394

    proj2 2013.06.18  0.00361  0.00361
    proj2 2013.06.19  0.00722   0.0108

    proj3 2013.06.18   0.0108   0.0108
    
  The columns are:
    - state name
    - date
    - time spent in that state on that date
    - total time spent in that state, up to and including of that date
  """

  result = ""
  periods = list(db.iter_periods())

  for state in states:
    durations = daily_durations(p for p in periods if p.state == state)
    total_time = datetime.timedelta(0)
    for date, time in sorted(durations.items()):
      total_time += time
      result += "{state} {date} {hours:8.2f} {total:8.2f}\n".format(
                  state=state, date=date.strftime("%Y.%m.%d"),
                  hours=time.total_seconds() / 3600.,
                  total=total_time.total_seconds() / 3600.)
    result += "\n"
  return result
