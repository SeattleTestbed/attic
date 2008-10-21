""" 
Author: Justin Cappos

Module: Polling program for GENI.   It looks for donations, sets them up, and
        writes the new info in the database.   

Start date: October 18th, 2008

This polls for resources donations in GENI.   It currently has lots and lots
of problems and was hurriedly written.   This will not recover correctly if 
it's interrupted when initializing a node, will not allow different owners
to donate resources from the same node.   This is a prime candidate for 
improvements or a rewrite.


"""
include time.repy
include nmclient.repy
include rsa.repy

import random
import advertise

# for time.sleep 
import time

# db api
import genidb

# the "happy meal" resources we will use...
baseresources = """
resource cpu .01
resource memory 15000000   # 15 MiB
resource diskused 8000000 # 8 MiB
resource events 5
resource filewrite 10000
resource fileread 10000
resource filesopened 2
resource insockets 2
resource outsockets 2
resource netsend 10000
resource netrecv 10000
resource loopsend 100000
resource looprecv 100000
resource lograte 3000
resource random 10
resource messport %s
resource messport %s
resource connport %s
resource connport %s
"""

# or load with rsa_file_to_publickey('genilookup.publickey')
genilookuppubkey = {'e':105218563213892243899209189701795214728063009020190852991629121981430129648590559454805294602863437180197383200157929797560056350651679990894183323458702862383371519103715161824514423932881746333116028227752248782962849181124520405658625393671898781069029621867416896240848133246870330371456213657364326213813, 'n':312714756092727515598780292379395872371276579078748109351554518254514481793368058883800678614580459772002765797032260325722225376614522500847276562927611577356613250215335341049455959290730180509179381157215997103098273389151149413304651001604934784742532791625955088398372313329455355494987750365806646536736636469629655380899143568352774219563065173996594667744415518391700387531919897253828997026843423501056159275468434318826550727964420829405894564122992335715124500381230290658083672331257499145017512885259835129381157750762124840076790791959202427846549512062536039325580240373309487741134319467890746673599741871268148060727018149256387697190931523693175768595351239154192239059676450669982991614136056253025495132755577907582430428560957011063839801600705947720544745078362907393070987536242330969100531923153182335864179094051994566951914233193211513835463083579669213012962131981383521706159377642531633316767375065073795772235104272775823159971873875983352843528481287521146512180790378064962825824780897817649973221317403460404503674474228769268269759375408409701974795615072086988269846532097319019681202860566295633729260133667739837481809185531026939053693396561388528361977535344851490021470007393713971344577027977}

def pollvessels():

  # BUG: Does this need to be wrapped in rsa_publickey_to_string?
  nodelist = advertise.lookup(genilookuppubkey)

  for node in nodelist:
    host, portstring = node.split(':')
    port = int(portstring)

    try:
      thisnmhandle = nmclient_createhandle(host, port)
    except NMClientException,e:
      # we'll add to the failed list after the for loop...
      # I don't need to do anything if this fails since I know nothing about 
      # the node...
      continue

    # no matter what, destroy the handle when done.  (no data hanging around)
    try:

      try:
        retdict = nmclient_getvesseldict(thisnmhandle)
      except NMClientException,e:
        # Okay, so we couldn't get the dict.   We're skipping for the same
        # reason as above (know nothing, can't do anything)...
        continue

#(might need to wrap the nodekey in rsa_publickey_to_string)
      nodeID = retdict['nodekey']

      # look up the node info using its key.
      node = genidb.lookup_node(nodeID)
      
# I'm treating the donor table as a dict keyed by nodeID

      # We should do this if either the node is new, or if the node
      # failed during init last time
      if node is None or node.status == 'Initializing':

        # this will be a new row in the donor table or an update of an
        # 'Initializing' (previously failed initialization) node
        # record.  We'll write this out at the very end with a tx.
        newnode = {}
        newnode['version'] = retdict['version']
        newnode['ip'] = host
        newnode['port'] = port

        # all known public donor keys
        donor_keys = genidb.get_donor_keys()

        vesselstoconfigure = []
        # Now I need to look at the vessels on the node...
        for vesselname in retdict['vessels']:
          thisvessel = retdict['vessels'][vesselname]
#(might need to wrap in rsa_publickey_to_string)
          if thisvessel['userkeys'] == [ genilookuppubkey ]:
            # Okay, this is being donated.   Let's check to see who is donating
#(might need to wrap in rsa_publickey_to_string)
            if thisvessel['ownerkey'] not in donor_keys:
              # how odd.   I don't know the donor key.   Let's skip this
#(might need to wrap in rsa_publickey_to_string)
              print "Unknown donor key: "+thisvessel['ownerkey']+" with userkey indicating donation"
              continue

            # look up the donor keys here (the public key is thisvessel['ownerkey']...
            donor_privkey = genidb.get_donor_privkey(thisvessel['ownerkey'])
            
            if donor_privkey == None:
              print "Could not find a matching donot private key for vessel's owner key"
# should we raise some kind of error and die here? (fatal)
            else:
              donor_key['privatekey'] =  donor_privkey
              donor_key['publickey'] = thisvessel['ownerkey']

            if thisvessel['advertise'] == False:
              # why aren't we advertising?   (not fatal)
              print "Not advertising for: "+nodeID+"!"

            if thisvessel['status'] == "Started":
              # why is something running?   (not fatal)
              print "Running program in donated vessel on: "+nodeID+"!"

# Donors are per computer now.   They really should be per vessel instead...
            vesselstoconfigure.append(vesselname)

        # Couldn't find anything to do!
        if len(vesselstoconfigure) == 0:
          # hmm.   I don't know what they want to donate.   Let's skip this
          print "Can't find donated vessels on "+node
          continue

        elif len(vesselstoconfigure) > 1:
          # BUG: Hmm, more than one vessels to add.   Let's skip for now...
          # I'll need to handle this later since this might happen during 
          # recovery
          print "Multiple donated vessels on "+node
          continue

        else: # len(vesselstoconfigure) == 1:

          # if we were not interrupted during init last time, get a node key...
          if node is None:
            ret_new_keys = genidb.get_new_keys()
            if ret_new_keys == None:
              print "no more keys available in the genidb -- get_new_keys() failed"
# raise an error? (fatal)
              (newnode['owner_pubkey'], newnode['owner_privkey']) = ret_new_keys

          # Okay, I'm there with bells on.   Let's init!
          newnode['status'] = 'Initializing'

          # TX 1 -- update or add the node record before performing setupnode
          node = genidb.create_update_node(node,newnode,donor_key)

          (vessellist,extravessel) = setupnode(thisnmhandle,vesselstoconfigure[0],
                                               donor_key['publickey'], donor_key['privatekey'],
                                               newnode['owner_pubkey'], newnode['owner_privkey'])
          
          # TX 2 -- update status of node to 'Ready' and vessel-list only 
          genidb.add_node_vessels(node,'Ready',vessellist,extravessel)
          

      elif node.status == 'Ready' or node.status == 'Broken':
        # alive and well (apparently)
        genidb.update_node('Ready')
        continue

      else:
        # unknown status!!!
        print "Unknown status "+node.status+" of node "+nodeID

    finally:
      nmclient_destroyhandle(thisnmhandle)


def setupnode(nmhandle, vesselname, oldpubkey, oldprivkey, newpubkey, newprivkey):

  # set the private and public keys in the handle.   
  myhandleinfo = nmclient_get_handle_info(nmhandle)
  myhandleinfo['publickey'] = oldpubkey
  myhandleinfo['privatekey'] = oldprivkey
  nmclient_set_handle_info(nmhandle, myhandleinfo)

  # change the owner...
#(might not need to wrap the nodekey in rsa_publickey_to_string)
  nmclient_signedsay(nmhandle, "ChangeOwner", vesselname, rsa_publickey_to_string(newpubkey))

  
  # now, fix the handle to use the new key...
  myhandleinfo = nmclient_get_handle_info(nmhandle)
  myhandleinfo['publickey'] = newpubkey
  myhandleinfo['privatekey'] = newprivkey
  nmclient_set_handle_info(nmhandle, myhandleinfo)

  # I need to get the resource information so I know what I'm dealing with...
  resourcedata = nmclient_rawsay(nmhandle, "GetVesselResources",vesselname)

  usableports = get_usableports(resourcedata)


  # okay, time to divide this up into vessels of the right size...
  newvessels = []
  currentvessel = vesselname
  

  while True:

    # If we don't have enough ports, break
    if len(usableports) < 2:
      break

    # set up the resource data...
    resourcedata = baseresources % (str(usableports[0]),str(usableports[1]),str(usableports[0]),str(usableports[1]))

    # we used the first two elements
    usableports = usableports[2:]

    try:
      newvesselstring = nmclient_signedsay(nmhandle, "SplitVessel", currentvessel, resourcedata)
    except NMClientException,e:
      # I'm foolishly assuming this is because we've split it all we can...
      break
      
    
    # first item returned has the right size...
    newvessels.append(newvesselstring.split()[0])

    # now this is the bit we'll split
    currentvessel = newvesselstring.split()[1]


  # so, the currentvessel is left over...   Let's make the user the lookup key
  
  nmclient_signedsay(nmhandle, "ChangeUsers", currentvessel, rsa_publickey_to_string(genilookuppubkey))

  return newvessels
    



def get_usableports(resourcedata):

  connports = []
  messports = []

  for line in resourcedata.split('\n'):

    if line.startswith('resource'):
      (linejunk, resourcetype, value) = line.split()
      if resourcetype == 'connport':
        connports.append(value)
      if resourcetype == 'messport':
        messports.append(value)

  retlist = []
  for item in connports:
    if item in messports:
      retlist.append(item)

  random.shuffle(retlist)







def main():
  # initialize time via NTP
  time_updatetime(34612)

  while True:
    pollvessels()
    time.sleep(???)


if __name__ == '__main__':
  main() 
