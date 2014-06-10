
import os
import time

JIFFIES_PER_SECOND = 100.0

# Maps each field in /proc/{PID}/stat to an index
FIELDS = {
"pid":0,
"state":1,
"ppid":2,
"pgrp":3,
"session":4,
"tty_nr":5,
"tpgid":6,
"flags":7,
"minflt":8,
"cminflt":9,
"majflt":10,
"cmajflt":11,
"utime":12,
"stime":13,
"cutime":14,
"cstime":15,
"priority":16,
"nice":17,
"num_threads":18,
"itrealvalue":19,
"starttime":20,
"vsize":21,
"rss":22,
"rlim":23,
"startcode":24,
"endcode":25,
"startstack":26,
"kstkesp":27,
"kstkeoip":28,
"signal":29,
"blocked":30,
"sigignore":31,
"sigcatch":32,
"wchan":33,
"nswap":34,
"cnswap":35,
"exit_signal":36,
"processor":37,
"rt_priority":38,
"policy":39,
"delayacct_blkio_ticks":40
}


pid = os.fork()
isChild = (pid == 0)

if isChild:
  start = time.time()
  while time.time() - start < 5:
    num = 5 ** 5
  exit()
else:
  time.sleep(6)
    
# Get the file in proc
fileh = open("/proc/"+str(pid)+"/stat","r")

# Read in all the data
data = fileh.read()

# Close the file handle
fileh.close()

# Strip the newline
data = data.strip("\n")

# Remove the substring that says "(python)", since it changes the field alignment
startIndex = data.find("(")
endIndex = data.find(")",startIndex)
data = data[:startIndex-1] + data[endIndex+1:]

# Break the data into an array by spaces
dataArr = data.split(" ")

print "utime",dataArr[FIELDS["utime"]]
print "stime",dataArr[FIELDS["stime"]]

print "CPU time", (int(dataArr[FIELDS["utime"]])+int(dataArr[FIELDS["stime"]]))/JIFFIES_PER_SECOND

# Print each field
#for (field, index) in FIELDS.items():
#  print field,dataArr[index]
