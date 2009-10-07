# checks if httpretrieave raise exception when the http server sends error
# msg's. This tests error msgs 202, 500, 400, and 404. httpretrieve raises
# an exception in the same format so this is ment to test the majority of
# the status code errors

# prints failed error msg if httpretrieve fails the test and excutes without printing
# if the test pass's



include httpretrieve.repy
include waitforwebserver.repy



def server_test_errormsg(httprequest_dictionary):
  # raises an exception depending up on the change_error_numb(which is used as a signal
  # for the count on the httpretrieve request) 
  change_error_numb = mycontext['change_error_numb']

  if change_error_numb == 1:
    raise HttpError202()  
  elif change_error_numb == 2:
    raise HttpError500()
  elif change_error_numb == 3:
    raise HttpError400()
  else:
    raise HttpError404()



if callfunc == 'initialize':

  try: 
    # build temp server that sends random error msg for client requests   
    waitforwebserverconn('http://127.0.0.1:12345', server_test_errormsg)
  except Exception, e:
    raise Exception('server raised a different error msg ' + str(e))  

  # make multiple requests to server using httpretrieve to see if it raises an exception for different
  # http error responses messages

  # used to change the error msg after each exception
  mycontext['change_error_numb'] = 0
  
  while True:
    # change the error number  
    mycontext['change_error_numb'] += 1
    try:
      # should raise an exception depending up on the change_error_numb
      recv_msg = httpretrieve_get_string('http://127.0.0.1:12345/')

    # catch the right exception depending up on the change_error_numb
    except HttpError202:
      if mycontext['change_error_numb'] != 1:
        print 'Failed: raised a HttpError202 when the server didnt send a HttpError202' 
        break
      pass
    except HttpError500:
      if mycontext['change_error_numb'] != 2:
        print 'Failed: raised a HttpError500 when the server didnt send a HttpError500'
        break
      pass
    except HttpError400:
      if mycontext['change_error_numb'] != 3:
        print 'Failed: raised a HttpError400 when the server didnt send a HttpError400'
        break
      pass
    except HttpError404:
      if mycontext['change_error_numb'] != 4:
        print 'Failed: raised a HttpError404 when the server didnt send a HttpError404'
      # last exception break the loop 
      break
    except Exception, e:
      # print a filed msg if the server raises a different exception
      print 'Failed: didnt raise right ecxeption'   
      break

    # if any one of the errors excute without raising an exception, print failed msg     
    else:
      print 'Failed: should have raised an exception because the server sent a http error'

  # done test failed (should stop the server over here)  
   

      
