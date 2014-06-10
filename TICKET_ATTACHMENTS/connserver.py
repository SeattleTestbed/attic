#!/usr/bin/env python

"""
A simple echo server
"""

import socket

host = ''
port = 12345
backlog = 5
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
while 1:
    client, address = s.accept()
    amountsent = 0
    while True:
      try:
        data = client.recv(size)
      except Exception, e:
        print 'recv',e
        data = ''
      amountsent = amountsent + len(data)
      if data:
          try:
            client.send(data)
          except Exception, e:
            print 'send',e
            data = ''
            
      if not data:
          print "closing with", amountsent
          client.close() 
          break

