

import ctypes
import ctypes.util
import time
import os

PID = os.fork()
isChild = (PID == 0)

if isChild:
  start = time.time()
  while (time.time() - start) < 5:
    num = 2 **32
  exit()
else:
  time.sleep(4)

def get_ctypes_error():
  errnoPointer = ctypes.cast(libc.errno, ctypes.POINTER(ctypes.c_int32))
  errVal = errnoPointer.contents
  return errVal.value

# Get the standard library
libc = ctypes.CDLL(ctypes.util.find_library("c"))

# Constants
PROC_PIDTASKINFO = 4

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
              
PROC_TASKINFO_SIZE = ctypes.sizeof(proc_taskinfo)

# "Cast" call to calloc
libc.calloc.restype = ctypes.POINTER(proc_taskinfo)
tinfo_ptr = libc.calloc(1, PROC_TASKINFO_SIZE)

nb = libc.proc_pidinfo(PID, PROC_PIDTASKINFO, ctypes.c_uint64(0),  tinfo_ptr, PROC_TASKINFO_SIZE) 

# Check for an error
if nb == 0:
  errornum = get_ctypes_error()
  print errno, ctypes.cast(libc.strerror(errornum), ctypes.c_char_p)

else:
  tinfo = tinfo_ptr.contents
  
  print tinfo.pti_total_user/1000000000.0, tinfo.pti_total_system/1000000000.0
  totalTime = tinfo.pti_total_user/1000000000.0 + tinfo.pti_total_system/1000000000.0
  
  print totalTime

libc.free(tinfo_ptr)

