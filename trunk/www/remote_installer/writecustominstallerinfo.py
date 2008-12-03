""" 
Author: Justin Cappos

Module: Writes the state for the custom installer...

Start date: October 20th, 2008

This initializes the custom installer for Seattle.   It sets up the starting 
resource files, creates the necessary dictionaries, creates a vesseldict, etc.

This is a bit of a mess, but the work is really a bunch of little things...

"""

# need to load public keys
include rsa.repy

import sys

import os

import persist

import nmresourcemath


import shutil


# The vesselcreationinfo has the following format:
#   [(vessel percent, ownerpubkeyfilename, list of user pubkeyfilenames),
#   (vessel percent, ownerkey, list of userpubkeyfilenames), ...]
#
# So it might look like:
#   [(1,'joe.publickey',[]),(5,'jim.publickey',['alice.publickey',
#   'bob.publickey']), (2, 'alice.publickey', [])]
#
# This would indicate v1 is owned by joe and gets 1 percent, v2 is owned
# by jim has users alice and bob and gets 5 percent, v3 is owned by
# alice and gets 2 percent.   I'll track the seattle information and
# will write it independently.
def create_installer_state(vesselcreationinfo, targetdirectory):



  # check the input...
  total = 0
  for item in vesselcreationinfo:
    if item[0] not in [1,2,3,4,5,6,7,8]:
      raise ValueError, "Invalid vessel percent '"+str(item[0])+"'"
    total = total + item[0]

  if total != 8:
    raise ValueError, "Total of vessel percents is '"+str(total)+"', not 8!"




  # keep a dictionary mapping filenames to public keys.   Add seattle to 
  # start with...
  keydict = {'seattle.publickey':rsa_file_to_publickey('seattle.publickey')}

  # then all of the other keys...
  for item in vesselcreationinfo:

    # if the owner is not in the dictionary...
    if item[1] not in keydict:
      keydict[item[1]] = rsa_file_to_publickey(item[1])

    # for user in the userlist...
    for userpubkeyfn in item[2]:
      if userpubkeyfn not in keydict:
        keydict[userpubkeyfn] = rsa_file_to_publickey(userpubkeyfn)




  vesseldict = {}
  vesselnumber = 1
  # time to work on the vessel dictionary...
  for item in vesselcreationinfo:

    vesselname = 'v'+str(vesselnumber)
    userkeylist = []
    for keyfn in item[2]:
      userkeylist.append(keydict[keyfn])

    vesseldict['v'+str(vesselnumber)] = {'userkeys':userkeylist, 'ownerkey':keydict[item[1]], 'oldmetadata':None, 'stopfilename':vesselname+'.stop', 'logfilename':vesselname+'.log', 'statusfilename':vesselname+'.status', 'resourcefilename':'resource.'+vesselname, 'advertise':True, 'ownerinformation':'', 'status':'Fresh'}
    vesselnumber = vesselnumber + 1
    

  # write the seattle vessel
  vesselname = 'v'+str(vesselnumber)
  vesseldict['v'+str(vesselnumber)] = {'userkeys':[], 'ownerkey':keydict['seattle.publickey'], 'oldmetadata':None, 'stopfilename':vesselname+'.stop', 'logfilename':vesselname+'.log', 'statusfilename':vesselname+'.status', 'resourcefilename':'resource.'+vesselname, 'advertise':True, 'ownerinformation':'', 'status':'Fresh'}
  
  persist.commit_object(vesseldict,targetdirectory+"/vesseldict")
    





  # I'm going to do the resources / restrictions now...
  
  oneeighth = nmresourcemath.read_resources_from_file('resources.oneeighth')
  offcut = nmresourcemath.read_resources_from_file('resources.offcut')
  restrictionsfo = file('vessel.restrictions')
  restrictionsstring = restrictionsfo.read()
  restrictionsfo.close()

  # I'll use this to figure out which ports to assign
  usedpercent = 0

  vesselnumber = 1

  for item in vesselcreationinfo:

  
    # make a resource file of the right size...
    size = item[0]
    thisresourcedata = oneeighth.copy()
    while size > 1:
      thisresourcedata = nmresourcemath.add(thisresourcedata, offcut)
      thisresourcedata = nmresourcemath.add(thisresourcedata, oneeighth)
      size = size - 1

    # I need the ports...
    startpercent = usedpercent
    endpercent = usedpercent+item[0]
    # a yucky way of getting the ports.   Should do 63100-63109 for the first,
    # 63110-63119 for the second, etc.
    thisresourcedata['messport'] = set(range(63100+10*startpercent, 63100+10*endpercent))
    thisresourcedata['connport'] = set(range(63100+10*startpercent, 63100+10*endpercent))
      
    nmresourcemath.write_resource_dict(thisresourcedata, targetdirectory+"/resource.v"+str(vesselnumber))
    
    # append the restrictions data.
    restrictionsfo = file(targetdirectory+'/resource.v'+str(vesselnumber),"a")
    restrictionsfo.write(restrictionsstring)
    restrictionsfo.close()

    # increment the vesselnumber and used percent
    vesselnumber = vesselnumber + 1
    usedpercent = usedpercent + item[0]
    
    
  # I'll copy the seattle resource file
  shutil.copy('resources.seattle',targetdirectory+'/resource.v'+str(vesselnumber))


  # make the directories...

  for num in range(len(vesselcreationinfo)+1):
    vesselname = 'v'+str(num+1)
    try:
      WindowsError

    except NameError: # not on windows...
      # make the vessel dirs...
      try:
        os.mkdir(targetdirectory+"/"+vesselname)
      except OSError,e:
        if e[0] == 17:
          # directory exists
          pass
        else:
          raise

    else: # on Windows...

      # make the vessel dirs...
      try:
        os.mkdir(targetdirectory+"/"+vesselname)
      except (OSError,WindowsError),e:
        if e[0] == 17 or e[0] == 183:
          # directory exists
          pass
        else:
          raise


  # and we're done!
  



def read_vesselinfo_from_file(filename):
  retvesselinfo = []
  lastvesseldata = None
  for line in open(filename):

    if line.split()[0] == 'Percent':
      if lastvesseldata:
        if lastvesseldata[1] == None:
          raise Exception, "Error, must have Owner for each vessel"
        retvesselinfo.append(lastvesseldata)
      lastvesseldata = [int(line.split()[1]), None, []]
    elif line.split()[0] == 'Owner':
      lastvesseldata[1] = line.split()[1]
    elif line.split()[0] == 'User':
      lastvesseldata[2].append(line.split()[1])
 

  retvesselinfo.append(lastvesseldata)
  return retvesselinfo

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Wrong number of arguments"
    print "Usage: python writecustominstallerinfo.py datafile targetdir"
    sys.exit(1)
  

  create_installer_state(read_vesselinfo_from_file(sys.argv[1]), sys.argv[2])
