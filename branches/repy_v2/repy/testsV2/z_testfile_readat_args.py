"""
This unit test checks the file.readat() argument.

We check:
  1) Input sanity checking
  2) SeekPastEndOfFile is raised
"""

def tryit(sizelimit, offset):
  try:
    fileh.readat(sizelimit, offset)
  except RepyArgumentError:
    pass
  else:
    print "Readat with sizelimit: "+str(sizelimit)+" and offset: "+str(offset)+" should have error!"

# Open a file
fileh = openfile("repy.py", False)

# Try some stuff
tryit(-1,0)
tryit(0,-1)
tryit(None, 0)
tryit(1, None)

# Try to seek past the end
try:
  fileh.readat(8, 500000)
  print "Read past then EOF!"
except SeekPastEndOfFileError:
  pass

# Close the file
fileh.close()



