#! /usr/bin/env python

import timeclock

def catch_typos(given, recognized):
  """Correct any mis-capitalized names, and remark on new ones.

  Arguments:
  - given: a mutable sequence of strings
  - recognized: a container of strings

  If any element of the given sequence matches a recognized string in
  all but case, its case will be corrected, and a message printed. If
  any element of the given sequence is not recognized, a message will
  be printed (in case the user mis-typed something).
  """
  translations = dict((p.upper(), p) for p in recognized)
  for i, project in enumerate(given):
    upper = project.upper()
    if project not in recognized:
      if upper in translations:
        new = translations[upper]
        print "Changing {old!r} to {new!r}".format(old=project, new=new)
        given[i] = translations[upper]
      else:
        print "New project: {!r}".format(project)


args = timeclock.parser.parse_args()

# If we're just reporting on the info in the database, open read-only;
# otherwise, we're recording, so we'll want to append to it.
mode = "r" if args.reporting == "REPORT" else "a+"
with open(args.file, mode) as f:
  db = timeclock.persistence.Database(f)

  last = db.last_state()
  if (last is not None) and last != timeclock.IDLE:
    print ("Refusing to run: last state in log is not Idle.\n"
           "Last instance may have crashed, or still be running.")
    exit(1)

  # First order of business, try to catch any typos the user made.
  projects = list(args.projects)
  catch_typos(projects, db.states())

  if args.reporting:
    print timeclock.reports.build_report_string(db, projects)
    exit(0)
  else:
    try:
      timeclock.gui.run_record_gui(db, projects,
                                   remind_time=args.remind_time,
                                   quiet=args.quiet)
    finally:
      # When we quit the program, no matter what, mark us as idle.
      try:
        db.write_change(timeclock.IDLE)
      except Exception, e:
        # Some error prevented us from editing the file.
        # Remark on it, then reraise the exception.
        print "Error:", e
        print "Failed to mark as idle."
        raise
