include tcp.repy

if callfunc == 'initialize':
  IP = getmyip()
  PORT = 12345
  MESSAGE = "hi"
  MAXLEN = 4096

  socket = Connection()
  socket.bind(IP, PORT)

if callfunc == 'initialize':

  socket.connect(IP, PORT)
  bytes = socket.send(MESSAGE)
  if bytes == 0:
    print "Expected some bytes"

  mess = socket.recv(MAXLEN)
  if mess != MESSAGE:
    print "%s != %s" % (mess, MESSAGE)

  socket.disconnect()
  exitall()
