""" 
<Author>
  Justin Cappos
  Ivan Beschastnikh (12/24/08) -- added usage
  Brent Couvrette   (2/27/09) -- added servicelog commandline option
  Conrad Meyer (5/22/09) -- switch option parsing to getopt

<Start Date>
  June 26th, 2008

<Description>
  Restricted execution environment for python.  Should stop someone
  from doing "bad things" (which is also defined to include many
  useful things).  This module allows the user to define code that
  gets called either on the reciept of a packet, when a timer fires,
  on startup, and on shutdown.  The restricted code can only do a few
  "external" things like send data packets and store data to disk.
  The CPU, memory, disk usage, and network bandwidth are all limited.

<Usage>
  Usage: repy.py [options] restrictionsfile.txt program_to_run.py [program args]

  Where [options] are some combination of the following:

  --simple               : Simple execution mode -- execute and exit
  --ip IP                : This flag informs Repy that it is allowed to bind to the given given IP.
                         : This flag may be asserted multiple times.
                         : Repy will attempt to use IP's and interfaces in the order they are given.
  --iface interface      : This flag informs Repy that it is allowed to bind to the given interface.
                         : This flag may be asserted multiple times.
  --nootherips           : Instructs Repy to only use IP's and interfaces that are explicitly given.
                         : It should be noted that loopback (127.0.0.1) is always permitted.
  --logfile filename.txt : Set up a circular log buffer and output to logfilename.txt
  --stop filename        : Repy will watch for the creation of this file and abort when it happens
                         : File can have format EXITCODE;EXITMESG. Code 44 is Stopped and is the default.
                         : EXITMESG will be printed prior to exiting if it is non-null.
  --status filename.txt  : Write status information into this file
  --cwd dir              : Set Current working directory
  --servicelog           : Enable usage of the servicelogger for internal errors
"""


# Let's make sure the version of python is supported
import checkpythonversion
checkpythonversion.ensure_python_version_is_supported()

import safe
import sys
import getopt
import emulfile
import emultimer
import emulcomm
import emulmisc
import idhelper
import nanny
import restrictions
import time
import threading
import logging

import nmstatusinterface

import nonportable

import statusstorage

import repy_constants   

import os

## we'll use tracebackrepy to print our exceptions
import tracebackrepy



# This block allows or denies different actions in the safe module.   I'm 
# doing this here rather than the natural place in the safe module because
# I want to keep that module unmodified to make upgrading easier.

# Allow the user to do try, except, finally, etc.
safe._NODE_CLASS_OK.append("TryExcept")
safe._NODE_CLASS_OK.append("TryFinally")
safe._NODE_CLASS_OK.append("Raise")
safe._NODE_CLASS_OK.append("ExcepthandlerType")
safe._NODE_CLASS_OK.append("Invert")
# needed for traceback
# NOTE: still needed for tracebackrepy
safe._BUILTIN_OK.append("isinstance")
safe._BUILTIN_OK.append("BaseException")
safe._BUILTIN_OK.append("WindowsError")
safe._BUILTIN_OK.append("type")
safe._BUILTIN_OK.append("issubclass")
# needed for socket ops and other things...   These should be safe, right?
safe._BUILTIN_OK.append("getattr")
safe._BUILTIN_OK.append("hasattr")
safe._BUILTIN_OK.append("setattr")
# needed to allow primitive marshalling to be built
safe._BUILTIN_OK.append("ord")
safe._BUILTIN_OK.append("chr")
# should not be used!   Use exitall instead.
safe._BUILTIN_OK.remove("exit")
safe._BUILTIN_OK.remove("quit")
# __repr__ should be harmless, but do we really want to add it?
safe._STR_OK.append("__repr__")
# allow __ in strings.   I'm 99% sure this is okay (do I want to risk it?)
safe._NODE_ATTR_OK.append('value')

# Disables safe, and resumes normal fork
def nonSafe_fork():
  val = __orig_fork()
  if val == 0 and safe._builtin_globals_r != None:
    safe._builtin_restore()
  return val

# Only override fork if it exists (e.g. Windows)
if "fork" in dir(os):  
  __orig_fork = os.fork
  os.fork = nonSafe_fork


# This is the user's program after parsing
usercode = None

# These are the functions and variables in the user's name space (along with 
# the builtins allowed by the safe module).   
usercontext = {
    'mycontext':{},                     # set up a place for them to store state
    'open':emulfile.emulated_open,      # emulated open function
    'file':emulfile.emulated_open,      # emulated file object
    'listdir':emulfile.listdir,         # List the files in the expts dir
    'removefile':emulfile.removefile,   # remove a file in the expts dir
    'getmyip':emulcomm.getmyip,         # provides an external IP
    'gethostbyname_ex':emulcomm.gethostbyname_ex, # same as socket method
    'recvmess':emulcomm.recvmess,       # message receive (UDP)
    'sendmess':emulcomm.sendmess,       # message sending (UDP)
    'openconn':emulcomm.openconn,       # reliable comm channel (TCP)
    'waitforconn':emulcomm.waitforconn, # reliable comm listen (TCP)
    'stopcomm':emulcomm.stopcomm,       # stop receiving (TDP/UDP)
    'settimer':emultimer.settimer,      # sets a timer
    'canceltimer':emultimer.canceltimer,# stops a timer if it hasn't fired
    'sleep':emultimer.sleep,            # blocks the thread for some time
    'randomfloat':emulmisc.randomfloat, # same as random.random()
    'getruntime':emulmisc.getruntime,   # amount of time the program has run
    'getlock':emulmisc.getlock,         # acquire a lock object
    'exitall':emulmisc.exitall          # Stops executing the sandboxed program
}



# There is a "simple execution" mode where there is a single entry into the
# code.   This is used only for testing python vs repy in the unit tests
# The simpleexec variable indicates whether or not simple execution mode should
# be used...
#simpleexec = None


def main(restrictionsfn, program, args):
  global usercontext
  global usercode
  global simpleexec

  # Armon: Initialize the circular logger before forking in init_restrictions()
  if logfile:
    # time to set up the circular logger
    loggerfo = logging.circular_logger(logfile)
    # and redirect err and out there...
    sys.stdout = loggerfo
    sys.stderr = loggerfo
  else:
    # let's make it so that the output (via print) is always flushed
    sys.stdout = logging.flush_logger(sys.stdout)
    
  # start the nanny up and read the restrictions files.  
  restrictions.init_restrictions(restrictionsfn)

  # Armon: Update our IP cache
  emulcomm.update_ip_cache()
      
  # grab the user code from the file
  usercode = file(program).read()

  # In order to work well with files that may contain a mix of \r\n and \n
  # characters (see ticket #32), I'm going to replace all \r\n with \n
  usercode = usercode.replace('\r\n','\n')

  # If we are in "simple execution" mode, execute and exit
  if simpleexec:
    safe.safe_exec(usercode,usercontext)
    sys.exit(0)


  # I'll use this to detect when the program is idle so I know when to quit...
  idlethreadcount =  threading.activeCount()

  # call the initialize function
  usercontext['callfunc'] = 'initialize'
  usercontext['callargs'] = args[:]

  initialize_id = idhelper.getuniqueid()
  try:
    nanny.tattle_add_item('events', initialize_id)
  except Exception, e:
    tracebackrepy.handle_internalerror("Failed to aquire event for '" + \
        "initialize' event.\n(Exception was: %s)" % e.message, 140)

  try:
    safe.safe_exec(usercode,usercontext)
  except SystemExit:
    raise
  except:
    # I think it makes sense to exit if their code throws an exception...
    tracebackrepy.handle_exception()
    nonportable.harshexit(6)
  finally:
    nanny.tattle_remove_item('events', initialize_id)


  # I've changed to the threading library, so this should increase if there are
  # pending events
  while threading.activeCount() > idlethreadcount:
    # do accounting here?
    time.sleep(1)


  # Once there are no more pending events for the user thread, we give them
  # an "exit" event.   This allows them to clean up, etc. if needed.

  # call the user program to notify them that we are exiting...
  usercontext['callfunc'] = 'exit'
  usercontext['callargs'] = (None,)

  exit_id = idhelper.getuniqueid()
  try:
    nanny.tattle_add_item('events', exit_id)
  except Exception, e:
    tracebackrepy.handle_internalerror("Failed to aquire event for '" + \
        "exit' event.\n(Exception was: %s)" % e.message, 141)

  try:
    # Armon: for the second run of the user code there is no reason to re do the
    # safety check, so by just doing a safe_run() we can save some time and memory
    safe.safe_run(usercode,usercontext)
  except SystemExit:
    raise
  except:
    # I think it makes sense to exit if their code throws an exception...
    tracebackrepy.handle_exception()
    nonportable.harshexit(7)
  finally:
    nanny.tattle_remove_item('events', exit_id)

  # normal exit...
  nonportable.harshexit(0)


def usage(str_err=""):
  # Ivan 12/24/2008
  """
   <Purpose>
      Prints repy.py usage and possibly an error supplied argument
   <Arguments>
      str_err (string):
        Options error to print to stdout
   <Exceptions>
      None
   <Side Effects>
      Modifies stdout
   <Returns>
      None
  """
  print
  if str_err:
    print "Error:", str_err
  print """
Usage: repy.py [options] restrictionsfile.txt program_to_run.py [program args]

Where [options] are some combination of the following:

--simple               : Simple execution mode -- execute and exit
--ip IP                : This flag informs Repy that it is allowed to bind to the given given IP.
                       : This flag may be asserted multiple times.
                       : Repy will attempt to use IP's and interfaces in the order they are given.
--iface interface      : This flag informs Repy that it is allowed to bind to the given interface.
                       : This flag may be asserted multiple times.
--nootherips           : Instructs Repy to only use IP's and interfaces that are explicitly given.
                       : It should be noted that loopback (127.0.0.1) is always permitted.
--logfile filename.txt : Set up a circular log buffer and output to logfilename.txt
--stop filename        : Repy will watch for the creation of this file and abort when it happens
                       : File can have format EXITCODE;EXITMESG. Code 44 is Stopped and is the default.
                       : EXITMESG will be printed prior to exiting if it is non-null.
--status filename.txt  : Write status information into this file
--cwd dir              : Set Current working directory
--servicelog           : Enable usage of the servicelogger for internal errors
"""
  return


if __name__ == '__main__':
  global simpleexec
  global logfile

  # Armon: The CMD line path to repy is the first argument
  repy_location = sys.argv[0]

  # Get the directory repy is in
  repy_directory = os.path.dirname(repy_location)
  
  # Translate into an absolute path
  if os.path.isabs(repy_directory):
    absolute_repy_directory = repy_directory
  
  else:
    # This will join the currect directory with the relative path
    # and then get the absolute path to that location
    absolute_repy_directory = os.path.abspath(os.path.join(os.getcwd(), repy_directory))
  
  # Store the absolute path as the repy startup directory
  repy_constants.REPY_START_DIR = absolute_repy_directory
  
  args = sys.argv[1:]

  try:
    optlist, fnlist = getopt.getopt(args, '', [
      'simple', 'ip=', 'iface=', 'nootherips', 'logfile=',
      'stop=', 'status=', 'cwd=', 'servicelog'
      ])

  except getopt.GetoptError:
    usage()
    sys.exit(1)

  # Set up the simple variable if needed
  simpleexec = False

  # By default we don't want to use the service logger
  servicelog = False

  # Default logfile (if the option --logfile isn't passed)
  logfile = None

  # Default stopfile (if the option --stopfile isn't passed)
  stopfile = None

  # Default stopfile (if the option --stopfile isn't passed)
  statusfile = None

  if len(fnlist) < 2:
    usage("Must supply a restrictions file and a program file to execute")
    sys.exit(1)

  for option, value in optlist:
    if option == '--simple':
      simpleexec = True

    elif option == '--ip':
      emulcomm.user_ip_interface_preferences = True

      # Append this ip to the list of available ones if it is new, since
      # multiple IP's may be specified
      if (True, value) not in emulcomm.user_specified_ip_interface_list:
        emulcomm.user_specified_ip_interface_list.append((True, value))

    elif option == '--iface':
      emulcomm.user_ip_interface_preferences = True
      
      # Append this interface to the list of available ones if it is new
      if (False, value) not in emulcomm.user_specified_ip_interface_list:
        emulcomm.user_specified_ip_interface_list.append((False, value))

    # Check if they have told us explicitly not to allow other IP's
    elif option == '--nootherips':
      # Set user preference to True
      emulcomm.user_ip_interface_preferences = True
      # Disable nonspecified IP's
      emulcomm.allow_nonspecified_ips = False
    
    elif option == '--logfile':
      # set up the circular log buffer...
      logfile = value

    elif option == '--stop':
      # Watch for the creation of this file and abort when it happens...
      stopfile = value

    elif option == '--status':
      # Write status information into this file...
      statusfile = value

    # Set Current Working Directory
    elif option == '--cwd':
      os.chdir(value)

    # Enable logging of internal errors to the service logger.
    elif option == '--servicelog':
      servicelog = True

  # Update repy current directory
  repy_constants.REPY_CURRENT_DIR = os.path.abspath(os.getcwd())

  # Initialize the NM status interface
  nmstatusinterface.init(stopfile, statusfile)
  
  # Write out our initial status
  statusstorage.write_status("Started")

  restrictionsfn = fnlist[0]
  progname = fnlist[1]
  progargs = fnlist[2:]

  # We also need to pass in whether or not we are going to be using the service
  # log for repy.  We provide the repy directory so that the vessel information
  # can be found regardless of where we are called from...
  tracebackrepy.initialize(progname, servicelog, absolute_repy_directory)

  try:
    main(restrictionsfn, progname, progargs)
  except SystemExit:
    nonportable.harshexit(4)
  except:
    tracebackrepy.handle_exception()
    nonportable.harshexit(3)
