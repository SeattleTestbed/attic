# Test wether or not a waitforconn can be opened after 
# a stopcomm has been called on a previous waitforconn of the same ip and port

# expected output: none

def new_client(remoteip, remoteport, socketlikeobj, commhandle, thisnatcon): 
  mycontext['count'] +=1

  
  

# run the test!
if callfunc == "initialize":
  
  ip = '127.0.0.1' 

  # a list of clients
  
  
  mycontext['count'] = 0
  handle = waitforconn(ip,12345,new_client)  


  sock1 = openconn(ip,12345)
  

  #THE FOLLOWING SHOULD HAVE THE SAME RESULT, BUT DON'T
  settimer(0,stopcomm,[handle])
  #stopcomm(handle)  


  sleep(2)
  try:
    sock2 = openconn(ip,12345)
  except Exception, e:
    error = e #just do nothing
  else:
    print 'failed to get error opening sock2'

  sleep(5)
  handle = waitforconn(ip,12345,new_client)
  sleep(5)

  sock3 = openconn(ip,12345)

 
  # exit the test
  exitall()
