README

<Program Name>

  reliable_client.repy
  reliable_server.repy

  reliable.repy

<Started>

  January 8, 2009



<Author>

  MikeMosh@cs.washington.edu

  Michael Moshofsky



<Purpose>

  reliable_client.repy reads data from a file and sends it to a server program 
  in a reliable way. The server program (reliable_server.repy) must be running 
  before reliable_client starts.



  The user can specify the time before packets are resent and
 also the number 
  of retries per packet. 

<Instructions>
  To use this program:
    First, run reliable_server.repy on a node. Enter in the filename where the
    data should be saved and the port that will be used. Make sure you write 
    down the ip address of the computer because you are going to need it for 
    reliable_client. 

    Next, run reliable_client.repy on another node. Enter the ip address for
    the server computer along with the other arguments in the format:
           filename serverip port maxdgramsize nretries timeoutms

    * Before doing this you must create a file with some data in it and specify
      the file name, so reliable_client.repy knows what to send.

    ** A way of testing the programs if you do not want to create a file or read 
       files. Have reliable_client.repy create a file with text in it at the start
       of the main method.

       This can be done with:
          # For testing purposes, creating a file with data to send.
          createfile = open(callargs[0], "w")
          print >> createfile, "abcd"
          createfile.close()

       Also you can add one line of code to the last line of reliable_server.repy 's 
       acknowledge_send method to print out the recieved data of the packet.

       This can be done with:
          print realmess
