import time
import random
import os

testfile = open("testfile", "a+")

rounds = 1024
filesize = 10 * 1024**3
blocksizelist = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048,
  4096, 8192, 16384, 32768, 65536, 2**17, 2**18, 2**19, 2**20] #, 2**21, 
#  2**22, 2**23, 2**24]
seeklist = []
sizelist = []

for i in range(0,rounds*len(blocksizelist)):
  seeklist.append(int(filesize * random.random()))
  # sizelist.append(min(int(filesize * random.random()), filesize - seeklist[-1])) # Could do random block sizes as well!


# random.shuffle(blocksizelist) # Decorrelate consecutive runs; not needed.

for j in blocksizelist:
  block = "." * j
  start1 = time.time()

  for (round, position) in zip(range(0,rounds), seeklist):
    #start2 = time.time()
    testfile.seek(position)
    testfile.write(block)
    testfile.flush()
    os.fsync(testfile) # Force OS to sync (cf PyDocs)
    #elapsed = time.time()-start2
    #print len(block), elapsed, len(block)/elapsed

  elapsed = time.time()-start1
  print len(block), elapsed, len(block)*rounds/elapsed, "OVERALL"



"""
for l in range(0,1):
  gstart = time.time()

  for k in range(0,1024):
    # mstart = time.time()

    for j in range(0,256):
      testfile.write(block)
      testfile.flush()
      os.fsync() # Force OS to sync (cf PyDocs)

    # elapsed = time.time()-mstart
    # print "M", elapsed, (1024*1024)/elapsed

  elapsed = time.time()-gstart
  print "G", elapsed, (1024*1024)/elapsed

elapsed = time.time()-start
"""