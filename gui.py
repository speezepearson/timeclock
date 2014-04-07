"Defines the GUI used by the timeclock program."

import sys
import subprocess
import Tkinter
from . import IDLE

class TimeclockFrame(Tkinter.Frame):
  """A Frame with radio buttons to select each of various states.

  When the radio button is changed, writes a change to a database.
  """
  def __init__(self, master, db, states, *args, **kwargs):
    Tkinter.Frame.__init__(self, master, *args, **kwargs)
    self.db = db
    self.real_states = list(states)
    self.states = self.real_states + [IDLE]
    self.state_variable = Tkinter.StringVar()
    self.state_variable.set(IDLE)
    for p in self.states:
      Tkinter.Radiobutton(self,     # Put the button in this window.
                          text=p,   # Label the button thus.
                          value=p,  # When clicked, write the name
                                    # into the following variable:
                          variable=self.state_variable,
                          command=self.radio_click
                          ).pack()  # Proceed to place button in window.
    Tkinter.Button(self, text="Distraction",
                   command=(lambda: self.after(60000, beep))).pack()

  def radio_click(self):
    """Respond to a possible change in state."""
    self.db.write_change(self.state_variable.get(), repeat=False)

  def remind(self, quiet=False, even_idle=False):
    """Subtly attract the user's attention by beeping and raising the window.

    If even_idle is False, and the current state is IDLE, don't do anything.
    If quiet is True, don't beep, just raise the window.
    """
    if (not even_idle) and self.state_variable.get() == IDLE:
      return
    
    try:
      if not quiet:
        beep()
      self.master.tkraise()
    except (NotImplementedError, OSError):
      pass  # If any of this isn't working, don't worry too much.

  def begin_reminding(self, period, quiet=False, even_idle=False):
    """Remind the user we're running every so often."""
    self.remind(quiet=quiet, even_idle=even_idle)
    seconds = 1000 # (Number of "after"-units in one second.)
    self.after(period*seconds, self.begin_reminding, period, quiet, even_idle)

def beep():
  """Make a discreet sound (on Linux or OS X) or raise NotImplementedError."""
  # (Making sounds is awfully system-dependent.  Good luck.)
  if sys.platform.startswith("linux"):
    subprocess.call(["aplay", "/usr/share/sounds/gtk-events/toggled.wav"])
  elif sys.platform.startswith("darwin"):
    subprocess.call(["afplay", "/System/Library/Sounds/Ping.aiff"])
  else:
    raise NotImplementedError("sounds not implemented on "+sys.platform)


def run_record_gui(db, states, remind_time=120, quiet=False):
  """Starts a Tk application and runs a timeclock in it."""
  root = Tkinter.Tk()
  root.title("Timeclock")
  root.iconname("Timeclock")
  tcf = TimeclockFrame(master=root, db=db, states=states)
  tcf.pack()
  if remind_time > 0:
    tcf.begin_reminding(period=remind_time, quiet=quiet)
  root.mainloop()   # All further activity is driven by clicks.
