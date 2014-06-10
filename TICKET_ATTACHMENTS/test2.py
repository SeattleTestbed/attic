
import socket
import time
import os

IP = "10.0.2.15"
#IP = "192.168.1.127"

if __name__ == "__main__":
  # Get socket 1
  sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock1.settimeout(5.0)
  sock1.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  sock1.bind((IP,50001))
  sock1.connect(("google.com",80))
  print sock1.gettimeout()
  
  # Get socket 2
  sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock2.settimeout(0.5)
  sock2.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  sock2.bind((IP,50002))
  sock2.connect(("yahoo.com",80))
  print sock2.gettimeout(), sock1.gettimeout()
  
  # Get socket 3
  sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock3.settimeout(None)
  sock3.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  sock3.bind((IP,50003))
  sock3.connect(("msn.com",80))
  print "All Sock Timeouts",sock3.gettimeout(), sock2.gettimeout(), sock1.gettimeout()
  
  # Try binding to the same sockets now
  
  # Get socket 4
  sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock4.settimeout(8.0)
  sock4.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  sock4.bind((IP,50001))
  
  # Get socket 5
  sock5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock5.settimeout(None)
  sock5.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  sock5.bind((IP,50002))
  
  # Try to recv from socket 2, socket 5 should not interfere
  try:
    sock2.recv(8)
  except Exception, e:
    print "Expect Timeout.",e
  else:
    print "Error! Should have exception."
    
  # Get socket 6
  sock6 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock6.settimeout(0.0001)
  sock6.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  sock6.bind((IP,50003))
  print "Old sock timeouts",sock3.gettimeout(), sock2.gettimeout(), sock1.gettimeout()
  print "New sock timeouts",sock6.gettimeout(), sock5.gettimeout(), sock4.gettimeout()
  


  
  