
import ctypes
import ctypes.util
import os
import time
import kinfo

PID = os.fork()
isChild = (PID == 0)

if isChild:
  start = time.time()
  while (time.time() - start) < 5:
    num = 2 **32
  exit()
else:
  time.sleep(4)

# Constants
CTL_KERN = 1
KERN_PROC = 14
KERN_PROC_PID = 1
#PID = os.getpid() # Override this to the child PID

# Get the Standard C library
libc = ctypes.CDLL(ctypes.util.find_library("c"))

# Get an array with 4 elements, set the syscall parameters
FourIntegers = ctypes.c_int * 4
mib = FourIntegers(CTL_KERN, KERN_PROC, KERN_PROC_PID, PID)

# Get kinfo structure, set the size
kp = kinfo.kinfo_proc(0)
size = ctypes.c_int(0)

status = libc.sysctl(mib, 4, None, ctypes.byref(size), None, 0)

# Make the syscall
status = libc.sysctl(mib, 4, ctypes.byref(kp), ctypes.byref(size), None, 0)

if status != 0:
  raise Exception, "Fatal Error, sysctl failed!"

# Calculate the numbers
ru = kp.ki_rusage

utime = ru.ru_utime.tv_sec + ru.ru_utime.tv_usec/1000000.0
stime = ru.ru_stime.tv_sec + ru.ru_stime.tv_usec/1000000.0

# Get the Resident Set size
mem = ru.ru_maxrss
print "RSS:",mem

ru = kp.ki_rusage_ch

utime_ch = ru.ru_utime.tv_sec + ru.ru_utime.tv_usec/1000000.0
stime_ch = ru.ru_stime.tv_sec + ru.ru_stime.tv_usec/1000000.0

print (utime, stime, utime_ch, stime_ch)
