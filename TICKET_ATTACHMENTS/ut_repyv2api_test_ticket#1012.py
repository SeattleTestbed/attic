"""
This unit test checks the sendmessage() API call.
Also shows that we can sendmessage using a port
that has active listening socket.
"""

#pragma repy
#pragma repy restrictions.twoports

server = listenformessage('127.0.0.1', 12345)
server1 = listenformessage('127.0.0.1', 12346)

data = "HI"*8
# send message from server1 to server
sendmessage('127.0.0.1', 12345, data, '127.0.0.1', 12346)

(rip, rport, mess) = server.getmessage()

server.close()
server1.close()

if mess != data:
  log("Mismatch!",'\n')
