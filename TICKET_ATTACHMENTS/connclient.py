import sys
callargs = sys.argv[1:]
import socket
myconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

myconn.connect((callargs[0], int(callargs[1])))

filedata = open(callargs[2]).read()
totalsenddata = filedata
chunksize =8
newdata = ''
while totalsenddata != '':
  senddata = totalsenddata[:chunksize]
  totalsenddata = totalsenddata[chunksize:]
  myconn.send(senddata)
  newdata = newdata + myconn.recv(len(senddata))

print newdata == filedata
myconn.close()
