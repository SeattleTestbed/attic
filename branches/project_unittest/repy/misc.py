
""" 
Author: Justin Cappos

Start Date: Sept 1st, 2008

Description:
Utility functions.   Broken out for use across different modules...


"""

import time 

import os

# This is for do_sleep
import nonportable

# sleep for a specified time.  Don't return early (no matter what)
def do_sleep(seconds):
  # Using getruntime() in lieu of time.time() because we want elapsed time 
  # regardless of the oddities of NTP
  start = nonportable.getruntime()
  sleeptime = seconds

  # return no earlier than the finish time
  finish = start + seconds

  while sleeptime > 0.0:
    time.sleep(sleeptime)
    now = nonportable.getruntime()

    # If sleeptime > 0.0 then I woke up early...
    sleeptime = finish - now


# check the disk space used by a dir.   Stolen from an implementation in 
# nonportable.py
def compute_disk_use(dirname):
  # Convert path to absolute
  dirname = os.path.abspath(dirname)
  
  diskused = 0
  
  for filename in os.listdir(dirname):
    try:
      diskused = diskused + os.path.getsize(os.path.join(dirname, filename))
    except IOError:   # They likely deleted the file in the meantime...
      pass
    except OSError:   # They likely deleted the file in the meantime...
      pass

    # charge an extra 4K for each file to prevent lots of little files from 
    # using up the disk.   I'm doing this outside of the except clause in
    # the failure to get the size wasn't related to deletion
    diskused = diskused + 4096
        
  return diskused


# MIX: Address this with repy <-> python integration instead
def getmyip():
  import socket
  # Open a connectionless socket
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  # Tell it to connect to google (we assume that the DNS entry for this works)
  # I've changed this to 80 because port 0 causes some systems (BSD / Mac) to
  # go nuts
  s.connect(('google.com', 80))

  # and the IP of the interface this connects on is the first item of the tuple
  (myip, localport) = s.getsockname()

  s.close()

  return myip


