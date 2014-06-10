from repyportability import *
import repyhelper
from time import sleep

repyhelper.translate_and_import('centralizedadvertise_v2.repy')
repyhelper.translate_and_import('parallelize.repy')

def announce(item):
  try:
    v2centralizedadvertise_announce(item, item, 600)
    return (getruntime(), None)
  except Exception, e:
    return (getruntime(), str(e))


def main():
  starttime = getruntime()

  items = range(20)
  phandle = parallelize_initfunction(items, announce, concurrentevents=50)

  # Wait for all the requests to complete
  while True:
    if parallelize_isfunctionfinished(phandle):
      break
    sleep(1)
  
  timings = []
  for success, results in parallelize_getresults(phandle).iteritems():
    timings.extend(results)

  parallelize_closefunction(phandle)
  
  for (thread_no, (timing, result)) in timings:
    print timing, result

  print "Operation took: ", getruntime() - starttime


main()