"""
Author: Armon Dadgar
Start Date: April 7th, 2009

Description:
  This file provides a python interface to low-level system call on the darwin (OSX) platform.
  It is designed to abstract away the C-level detail and provide a high-level method of doing
  common management tasks.

"""

import ctypes       # Allows us to make C calls
import ctypes.util  # Helps to find the C library

import os           # Provides some convenience functions
import time         # Used for time.time()

import nix_common_api as nix_api # Import the Common API

import textops      # Import seattlelib's textops library

import portable_popen  # Import for our custom Popen

# Manually import the common functions we want
exists_outgoing_network_socket = nix_api.exists_outgoing_network_socket
exists_listening_network_socket = nix_api.exists_listening_network_socket
get_available_interfaces = nix_api.get_available_interfaces

# Get the standard library
libc = ctypes.CDLL(ctypes.util.find_library("c"))

# Get libproc
libproc = ctypes.CDLL(ctypes.util.find_library("proc"))

# Global Variables

# Storing this information allows us to make a single call to update the structure,
# but provide information about multiple things. E.g.memory and CPU
# Without this, each piece of info would require a call
# Also allows us to only allocate memory once, rather than every call
last_proc_info_struct = None   # The last structure

# Functions
_calloc = libc.calloc
_free = libc.free

# Use libproc since Tiger does not include in libc
_proc_pidinfo = libproc.proc_pidinfo

# Constants
PROC_pidTASKINFO = 4
CTL_KERN = 1
KERN_BOOTTIME = 21
TwoIntegers = ctypes.c_int * 2 # C array with 2 ints

# Structures

# Provides the struct proc_taskinfo structure, which is used
# to retrieve information about a process by pid
class proc_taskinfo(ctypes.Structure):
  _fields_ = [("pti_virtual_size", ctypes.c_uint64),
              ("pti_resident_size", ctypes.c_uint64),
              ("pti_total_user", ctypes.c_uint64),
              ("pti_total_system", ctypes.c_uint64),
              ("pti_threads_user", ctypes.c_uint64),
              ("pti_threads_system", ctypes.c_uint64),
              ("pti_policy", ctypes.c_int32),
              ("pti_faults", ctypes.c_int32),
              ("pti_pageins", ctypes.c_int32),
              ("pti_cow_faults", ctypes.c_int32),
              ("pti_messages_sent", ctypes.c_int32),
              ("pti_messages_received", ctypes.c_int32),
              ("pti_syscalls_mach", ctypes.c_int32),
              ("pti_syscalls_unix", ctypes.c_int32),
              ("pti_csw", ctypes.c_int32),
              ("pti_threadnum", ctypes.c_int32),
              ("pti_numrunning", ctypes.c_int32),
              ("pti_priority", ctypes.c_int32)]

class timeval(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long),
                ("tv_usec", ctypes.c_long)]
              
# Store the size of this structure
PROC_TASKINFO_SIZE = ctypes.sizeof(proc_taskinfo)

# This functions helps to conveniently retrieve the errno
# of the last call. This is a bit tedious to do, since 
# Python doesn't understand that this is a globally defined int
def get_ctypes_errno():
  errno_pointer = ctypes.cast(libc.errno, ctypes.POINTER(ctypes.c_int32))
  err_val = errno_pointer.contents
  return err_val.value

# Returns the string version of the errno  
def get_ctypes_error_str():
  errornum = get_ctypes_errno()
  return ctypes.cast(libc.strerror(errornum), ctypes.c_char_p).value

def _cast_calloc_type(casttype):
  """
  <Purpose>
    Casts the return type of calloc. This is like doing (type*)calloc(...) in C
  
  <Arguments>
    type: The type to cast as.
  """
  _calloc.restype = casttype


def _get_proc_info_by_pid(pid):
  """
  <Purpose>
    Immediately updates the internal proc_taskinfo structure.
  
  <Arguments>
    pid: The Process Identifier for which data should be retrieved
  
  <Exceptions>
    Raises an Exception if there is an error.
  
  <Returns>
    Nothing
  """
  global last_proc_info_struct
  
  # Check if we need to allocate a structure
  if last_proc_info_struct is None:
    print "Creating last_proc_info_struct"
    # Cast calloc as a pointer to the proc_taskinfo structure
    _cast_calloc_type(ctypes.POINTER(proc_taskinfo))
    
    # Allocate a structure
    last_proc_info_struct = _calloc(1, PROC_TASKINFO_SIZE)
    print "Created struct: ",last_proc_info_struct
  
  # Make the call to update
  status = _proc_pidinfo(pid, PROC_pidTASKINFO, ctypes.c_uint64(0),  last_proc_info_struct, PROC_TASKINFO_SIZE)
  print "_proc_pid_info status: ",status, "struct size: ",PROC_TASKINFO_SIZE, "struct: ",last_proc_info_struct

  if status is 0:
    # This means to data was written, this is an error
    raise Exception,"Errno:"+str(get_ctypes_errno())+", Error: "+get_ctypes_error_str()


def get_process_cpu_time(pid):
  """
  <Purpose>
    Returns the total CPU time used by a process.
    
  <Arguments>
    pid: The process identifier for the process to query.
  
  <Exceptions>
    See _get_proc_info_by_pid.
  
  <Returns>
    The total cpu time.
  """
  global last_proc_info_struct
  
  # Update the info
  print "Updating struct"
  _get_proc_info_by_pid(pid)
  print "Finished updating struct"

  # Get the process info by dereferencing the pointer
  print "Dereferncing pointer to struct"
  proc_info = last_proc_info_struct.contents
  
  # Get the total time from the user time and system time
  # Divide 1 billion since time is in nanoseconds
  print "Calculating CPU Time"
  total_time = proc_info.pti_total_user/1000000000.0 + proc_info.pti_total_system/1000000000.0
  
  # Return the total time
  return total_time
  

def get_process_rss(force_update=False,pid=None):
  """
  <Purpose>
    Returns the Resident Set Size of a process. By default, this will
    return the information cached by the last call to _get_proc_info_by_pid.
    This call is used in get_process_cpu_time.
    
  <Arguments>
    force_update:
      Allows the caller to force a data update, instead of using the cached data.
    
    pid:
      If force_update is True, this parameter must be specified to force the update.
  
  <Exceptions>
    See _get_proc_info_by_pid.
    
  <Returns>
    The RSS of the process in bytes.
  """
  global last_proc_info_struct
  
  # Check if an update is being forced
  if force_update and pid != None:
    # Update the info
    _get_proc_info_by_pid(pid)
  
  # Get the process info by dereferencing the pointer
  proc_info = last_proc_info_struct.contents
  
  # Fetch the RSS
  rss = proc_info.pti_resident_size
  
  # Return the info
  return rss


# Return the timeval struct with our boottime
def _get_boottime_struct():
  # Get an array with 2 elements, set the syscall parameters
  mib = TwoIntegers(CTL_KERN, KERN_BOOTTIME)

  # Get timeval structure, set the size
  boottime = timeval()                
  size = ctypes.c_size_t(ctypes.sizeof(boottime))

  # Make the syscall
  retval = libc.sysctl(mib, 2, ctypes.pointer(boottime), ctypes.pointer(size), None, 0)
  assert(retval == 0)

  return boottime

def get_system_uptime():
  """
  <Purpose>
    Returns the system uptime.

  <Returns>
    The system uptime.  
  """
  # Get the boot time struct
  boottime = _get_boottime_struct()

  # Calculate uptime from current time
  uptime = time.time() - boottime.tv_sec

  return uptime

def get_uptime_granularity():
  """
  <Purpose>
    Determines the granularity of the get_system_uptime call.

  <Returns>
    A numerical representation of the minimum granularity.
    E.g. 2 digits of granularity would return 0.01
  """
  # Get the boot time struct
  boottime = _get_boottime_struct()

  # Check if the number of nano seconds is 0
  if boottime.tv_usec == 0:
    granularity = 0

  else:
    # Convert nanoseconds to string
    nanosecondstr = str(boottime.tv_usec)

    # Justify with 0's to 9 digits
    nanosecondstr = nanosecondstr.rjust(9,"0")

    # Strip the 0's on the other side
    nanosecondstr = nanosecondstr.rstrip("0")

    # Get granularity from the length of the string
    granularity = len(nanosecondstr)

  # Convert granularity to a number
  return pow(10, 0-granularity)

def get_system_thread_count():
  """
  <Purpose>
    Returns the number of active threads running on the system.
    
  <Returns>
    The thread count.
  """

  # Use PS since it is setuid and can get the info for us
  process = portable_popen.Popen(["ps", "axM"])
  
  ps_output, _ = process.communicate()

  # Subtract 1 from the number of lines because the first line is a a table
  # header: "  PID TTY      STAT   TIME COMMAND"
  threads = len(textops.textops_rawtexttolines(ps_output)) - 1
  
  return threads

def clean_up():
  """
  <Purpose>
    Allows the module to cleanup any internal state and release memory allocated.
  """
  global last_proc_info_struct
  
  # Check if last_proc_info_struct is allocated and free it if necessary
  if last_proc_info_struct != None:
    _free(last_proc_info_struct)



def get_interface_ip_addresses(interfaceName):
  """
  <Purpose>
    Returns the IP address associated with the interface.
  
  <Arguments>
    interfaceName: The string name of the interface, e.g. eth0
  
  <Returns>
    A list of IP addresses associated with the interface.
  """

  # Launch up a shell, get the feed back
  # We use ifconfig with the interface name.
  ifconfig_process = portable_popen.Popen(["/sbin/ifconfig", interfaceName.strip()])

  ifconfig_output, _ = ifconfig_process.communicate()
  ifconfig_lines = textops.textops_rawtexttolines(ifconfig_output)
  
  # Look for ipv4 addresses
  target_lines = textops.textops_grep("inet", ifconfig_lines)
  # and not ipv6
  target_lines = textops.textops_grep("inet6", target_lines, exclude=True)

  # Only take the ip(s)
  target_lines = textops.textops_cut(target_lines, delimiter=" ", fields=[1])

  # Create an array for the ip's
  ipaddressList = []
  
  for line in target_lines:
     # Strip the newline and any spacing
     line = line.strip("\n\t ")
     ipaddressList.append(line)

  # Done, return the interfaces
  return ipaddressList
