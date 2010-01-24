"""
This unit test checks that the limits returned by getresources() are valid.
It uses a specific restrictions file, so that what we check is in-sync with
that file.

We check that:
  1) No entries exist which are unexpected
  2) All entries return match the values we expect

"""

# Call getresources
limits, usage, stoptimes = getresources()

# Check the limits
expected = {"cpu":0.1,
            "memory":15000000,
            "diskused":100000000,
            "events":10,
            "filewrite":100000,
            "fileread":100000,
            "filesopened":5,
            "insockets":5,
            "outsockets":5,
            "netsend":10000,
            "netrecv":10000,
            "loopsend":1000000,
            "looprecv":1000000,
            "lograte":30000,
            "random":100,
            "messport":set([12345]),
            "connport":set([12345]),
           }

# Check everything
for resource in expected.keys():
  if resource not in limits:
    print "Resource '"+resource+"' not in limits!"
    continue

  expected_val = expected[resource]
  actual_val = limits[resource]

  if expected_val != actual_val:
    print "Mis-match between expected and actual values for resource '"+resource+"'!"
    print "Expected: "+str(expected_val)+" Actual: "+str(actual_val)


# Check for resources that we did not expect
for resource in limits.keys():
  if resource not in expected:
    print "getresources() limits provides '"+resource+"' which is not expected!"

