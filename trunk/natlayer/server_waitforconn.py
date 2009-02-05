include NATLayer.py

# Must be pre-processed by repypp
# Takes 1 argument, the server's MAC

def newClient(remotemac, socketlikeobj, thisnatcon):
  print "Connected Client: ",remotemac
  while True:
    data = socketlikeobj.recv(1024)
    if data != "":
      num = int(data)
      socketlikeobj.send(str(num+1))

if callfunc == "initialize":
  mac = callargs[0]
  print "Connecting..."
  natcon = NATConnection(mac, "127.0.0.1", 12345)
  natcon.initServerConnection(1024) # 1024 byte buffer
  print "Connected! Starting echo."
  
  natcon.waitforconn(newClient)
  
