def foo(ip,port,sockobj, ch,mainch):
  
  data = sockobj.recv(4096)

  if data != "Hello":
    print 'Error: data did not match "Hello"'
    exitall()

  sockobj.send("bye")

  stopcomm(mainch)
  stopcomm(ch)


if callfunc == 'initialize':

  ip = getmyip()

  waitforconn(ip,12345,foo)
  sleep(.1)
  sockobj = openconn(ip,12345)

  sockobj.send("Hello")

  data = sockobj.recv(4096)

  if data != "bye":
    print 'Error: data did not match "bye"'
    exit(1)

  sockobj.close()
