# if stopcomm is called twice on the same handle it 
# returns false.


def echo(rip,rport,sock,thish,lh):
  sock.close()


if callfunc == "initialize":
  
  ip = '127.0.0.1'
  waitport = 12345
  
 
  # the waitfor conn we will connect to
  handle = waitforconn(ip,waitport,echo)

  stopcomm(handle)
  stopped = stopcomm(handle)
  if stopped is not False:
    print 'stopcomm did not return False'
