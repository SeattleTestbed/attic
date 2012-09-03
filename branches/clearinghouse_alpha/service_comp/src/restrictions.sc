resource cpu .10
resource memory 25000000   # 15 Million bytes
resource diskused 100000000 # 100 MB
resource events 50
resource filewrite 10000
resource fileread 10000
resource filesopened 5
resource insockets 5
resource outsockets 5
resource netsend 10000
resource netrecv 10000
resource loopsend 1000000
resource looprecv 1000000
resource lograte 30000
resource random 100
resource messport 12345
resource messport 12347
resource connport 12345
resource connport 19999
resource connport 12346
resource connport 12347
resource connport 12348
resource connport 12349


call gethostbyname_ex allow
call sendmess allow
call stopcomm allow 			# it doesn't make sense to restrict
call recvmess allow
call openconn allow
call waitforconn allow
call socket.close allow 		# let's not restrict
call socket.send allow 			# let's not restrict
call socket.recv allow 			# let's not restrict
# open and file.__init__ both have built in restrictions...
call open arg 0 is junk_test.out allow 	# can write to junk_test.out
call open arg 1 is r allow 		# allow an explicit read
call open arg 1 is w allow
call open arg 1 is rb allow 		# allow an explicit read
call open noargs is 1 allow 		# allow an implicit read 
call file.__init__ arg 0 is junk_test.out allow # can write to junk_test.out
call file.__init__ arg 1 is r allow 	# allow an explicit read
call file.__init__ arg 1 is rb allow 	# allow an explicit read
call file.__init__ arg 1 is r+b allow 	
call file.__init__ arg 1 is w allow 	
call file.__init__ arg 1 is wb allow 	

call file.__init__ noargs is 1 allow 	# allow an implicit read 


call file.close allow 			# shouldn't restrict
call file.flush allow 			# they are free to use
call file.next allow 			# free to use as well...
call file.read allow 			# allow read
call file.readline allow 		# shouldn't restrict
call file.readlines allow 		# shouldn't restrict
call file.seek allow 			# seek doesn't restrict
call file.write allow 			# shouldn't restrict (open restricts)
call file.writelines allow 		# shouldn't restrict (open restricts)
call sleep allow			# harmless
call settimer allow			# we can't really do anything smart
call canceltimer allow			# should be okay
call exitall allow			# should be harmless 

call log.write allow
call log.writelines allow
call getmyip allow			# They can get the external IP address
call listdir allow			# They can list the files they created
call removefile allow			# They can remove the files they create
call randomfloat allow			# can get random numbers
call getruntime allow			# can get the elapsed time
call getlock allow			# can get a mutex
