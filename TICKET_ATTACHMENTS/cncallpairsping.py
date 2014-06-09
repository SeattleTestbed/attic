###INFORMATION###
#This is a modified version of all pairs ping designed to test the cnc system
#Unlike allpairsping.py, this code reads from a file that gives an available port on each neighbor as well as the ip

#Usage: cncallpairsping.py [no arguments]
#the file NEIGHBOR_INFO_FILE_NAME must list each neighbor on a separate line, where each neighbor is represented as a space separated ip port pair.

#begin include cncclient.repy
"""
<Author>
  Cosmin Barsan
  

<Purpose>
  The purpose is to provide a wrapper that repy programs can include 
  
<Usage>
  include in a repy program and call cncclient_initialize
  
  
<Dependencies>
  The cnc client wrapper requires the following files (from the cnc libraries):
  
  cncFileParser.repy
  cncSignData.repy
  keyrangelib.repy
  registration_server_list.txt - must list the registration server addresses and public keys in format specified in cncFileParser.repy

  
"""

#begin include time.repy
"""
   Author: Justin Cappos

   Start Date: 8 August 2008

   Description:

   This module handles getting the time from an external source.  It gets the
   remote time once and then uses the offset from the local clock from then on
   to return the current time.

   To use this module, first make a call to time_updatetime(localport) with a
   local UDP port that you have permission to send/recv on. This will
   contact some random subset of NTP servers to get and store the local time.

   Then, to get the actual time, call time_gettime() which will return
   the current time (in seconds). time_gettime() can be called at any point
   after having called time_updatetime(localport) since time_gettime() simply
   calculates how much time has elapsed since the local time was originally 
   acquired from one of the NTP servers.

   Note that time_gettime() will raise TimeError if no NTP server responded or
   if time_updatetime(localport) was never previously called.  If time_gettime()
   fails, then time_updatetime(localport) can be called again to sample time
   from another random set of NTP servers.
"""


# Use for random sampling...
#begin include random.repy
""" Random routines (similar to random in Python)
Author: Justin Cappos


"""

def random_randint(minvalue, maxvalue):

  if minvalue > maxvalue:
    # mimic random's failure behaviour
    raise ValueError, "empty range for randrange()"

  if maxvalue == minvalue:
    return maxvalue

  randomrange = maxvalue - minvalue

  # get a small random number
  randomnumber = int(randomfloat() * 2**32)

  # We're going to generate the number 32 bits at a time...
  while randomrange > 2**32:
    # add random bits to the bottom...
    randomnumber = (randomnumber << 32) + int(randomfloat() * 2**32)
    # shift the range
    randomrange = randomrange >> 32

  # BUG: doing mod here isn't perfect.   If there are 32 bits to make random,
  # and the range isn't a power of 2, some numbers will be slightly more likely
  # than others...   I could detect and retry I guess...
  retvalue = minvalue + (randomnumber % (maxvalue - minvalue + 1))
  assert(minvalue<=retvalue<=maxvalue)
  return retvalue


def random_sample(population, k):
  newpopulation = population[:]
  if len(population) < k:
    raise ValueError, "sample larger than population"

  retlist = []
  populationsize = len(population)-1

  for num in range(k):
    pos = random_randint(0,populationsize-num)
    retlist.append(newpopulation[pos])
    del newpopulation[pos]

  return retlist

#end include random.repy


class TimeError(Exception):
  pass


time_query_times = []

# See RFC 2030 (http://www.ietf.org/rfc/rfc2030.txt) for details about NTP

# this unpacks the data from the packet and changes it to a float
def time_convert_timestamp_to_float(timestamp):
  integerpart = (ord(timestamp[0])<<24) + (ord(timestamp[1])<<16) + (ord(timestamp[2])<<8) + (ord(timestamp[3]))
  floatpart = (ord(timestamp[4])<<24) + (ord(timestamp[5])<<16) + (ord(timestamp[6])<<8) + (ord(timestamp[7]))
  return integerpart + floatpart / float(2**32)

def time_decode_NTP_packet(ip, port, mess, ch):
  time_settime(time_convert_timestamp_to_float(mess[40:48]))
  stopcomm(ch)



def time_settime(currenttime):
  """
   <Purpose>
    Sets a remote time as the current time.

   <Arguments>
    currenttime:
               The remote time to be set as the current time.

   <Exceptions>
    None.

   <Side Effects>
    Adjusts the current time.

   <Returns>
    None.
  """

  time_query_times.append((getruntime(), currenttime))



#BUG: Do I need to compensate for the time taken to contact the time server?    (#353)
def time_updatetime(localport):
  """
   <Purpose>
    Obtains and stores the local time from a subset of NTP servers.

   <Arguments>
    localport:
             The local port to be used when contacting the NTP server(s).

   <Exceptions>
    TimeError when getmyip() fails or one of the subset of NTP servers will not
    respond.

   <Side Effects>
    time_settime(currenttime) is called as the subprocess of a subprocess, which
    adjusts the current time.

   <Returns>
    None.
  """

  try:
    ip = getmyip()
  except Exception, e:
    raise TimeError, str(e)

  timeservers = ["time-a.nist.gov", "time-b.nist.gov", "time-a.timefreq.bldrdoc.gov", "time-b.timefreq.bldrdoc.gov", "time-c.timefreq.bldrdoc.gov", "utcnist.colorado.edu", "time.nist.gov", "time-nw.nist.gov", "nist1.symmetricom.com", "nist1-dc.WiTime.net", "nist1-ny.WiTime.net", "nist1-sj.WiTime.net", "nist1.aol-ca.symmetricom.com", "nist1.aol-va.symmetricom.com", "nist1.columbiacountyga.gov", "nist.expertsmi.com", "nist.netservicesgroup.com"]

  startlen = len(time_query_times)
  listenhandle = recvmess(ip,localport, time_decode_NTP_packet)

  # always close the handle before returning...
  try: 
    # try five random servers times...
    for servername in random_sample(timeservers,5):

      # this sends a request, version 3 in "client mode"
      ntp_request_string = chr(27)+chr(0)*47
      try: 
        sendmess(servername,123, ntp_request_string, ip, localport) # 123 is the NTP port
      except Exception:
        # most likely a lookup error...
        continue

      # wait for 5 seconds for a response before retrying
      for junkiterations in range(10):
        sleep(.5)

        if startlen < len(time_query_times):
          # If we've had a response, we're done!
          return
    
    
  finally:
    stopcomm(listenhandle)

  # Failure, tried servers without luck...
  raise TimeError, "Time Server update failed.  Perhaps retry later..."



def time_gettime():
  """
   <Purpose>
    Gives the current time in seconds by calculating how much time has elapsed
    since the local time was obtained from an NTP server via the
    time_updatetime(localport) function.

   <Arguments>
    None.

   <Exceptions>
    TimeError when time_updatetime(localport)has not previously been called or 
    when time_updatetime(localport) has any unresolved TimeError exceptions.

   <Side Effects>
    None.

   <Returns>
    Current time in seconds.
  """

  if time_query_times == []:
    raise TimeError

  # otherwise use the most recent data...
  latest_update = time_query_times[-1]

  # first item is the getruntime(), second is NTP time...
  elapsedtimesinceupdate = getruntime() - latest_update[0]

  return latest_update[1] + elapsedtimesinceupdate



# in case you want to change to time since the 1970 (as is common)
time_seconds_from_1900_to_1970 = 2208988800


#end include time.repy
#begin include cncFileParser.repy
"""
<Library Name>
  cncFileParser.repy

<Started>
  March 31, 2009

<Author>
  Cosmin Barsan
  
<Purpose>
  Contains helper methods to read and write files containing data used by the update and registration servers

"""
#begin include rsa.repy
"""RSA module

Adapted by Justin Cappos from the version by:
author = "Sybren Stuvel, Marloes de Boer and Ivo Tamboer"
date = "2008-04-23"


All of the base64 encoding, pickling, and zlib encoding has been removed
"""


# NOTE: Python's modulo can return negative numbers. We compensate for
# this behaviour using the abs() function

#begin include random.repy
#already included random.repy
#end include random.repy

#begin include math.repy
""" Justin Cappos -- substitute for a few python math routines"""

def math_ceil(x):
  xint = int(x)
  
  # if x is positive and not equal to itself truncated then we should add 1
  if x > 0 and x != xint:
    xint = xint + 1

  # I return a float because math.ceil does
  return float(xint)



def math_floor(x):
  xint = int(x)
  
  # if x is negative and not equal to itself truncated then we should subtract 1
  if x < 0 and x != xint:
    xint = xint - 1

  # I return a float because math.ceil does
  return float(xint)



math_e = 2.7182818284590451
math_pi = 3.1415926535897931

# stolen from a link off of wikipedia (http://en.literateprograms.org/Logarithm_Function_(Python)#chunk use:logN.py)
# MIT license
#
# hmm, math_log(4.5,4)      == 1.0849625007211561
# Python's math.log(4.5,4)  == 1.0849625007211563
# I'll assume this is okay.
def math_log(X, base=math_e, epsilon=1e-16):
  # log is logarithm function with the default base of e
  integer = 0
  if X < 1 and base < 1:
    # BUG: the cmath implementation can handle smaller numbers...
    raise ValueError, "math domain error"
  while X < 1:
    integer -= 1
    X *= base
  while X >= base:
    integer += 1
    X /= base
  partial = 0.5               # partial = 1/2 
  X *= X                      # We perform a squaring
  decimal = 0.0
  while partial > epsilon:
    if X >= base:             # If X >= base then a_k is 1 
      decimal += partial      # Insert partial to the front of the list
      X = X / base            # Since a_k is 1, we divide the number by the base
    partial *= 0.5            # partial = partial / 2
    X *= X                    # We perform the squaring again
  return (integer + decimal)


#end include math.repy



def rsa_gcd(p, q):
    """Returns the greatest common divisor of p and q


    >>> gcd(42, 6)
    6
    """
    if p<q: return rsa_gcd(q, p)
    if q == 0: return p
    return rsa_gcd(q, abs(p%q))

def rsa_bytes2int(bytes):
    """Converts a list of bytes or a string to an integer

    >>> (128*256 + 64)*256 + + 15
    8405007
    >>> l = [128, 64, 15]
    >>> bytes2int(l)
    8405007
    """

    if not (type(bytes) is list or type(bytes) is str):
        raise TypeError("You must pass a string or a list")

    # there is a bug here that strings with leading \000 have the leading char
    # stripped away.   I need to fix that.  To fix it, I prepend \001 to 
    # everything I process.   I also have to ensure I'm passed a small enough
    # chunk that it all still fits (fix for that where I'm called).
    bytes = '\001' + bytes

    # Convert byte stream to integer
    integer = 0
    for byte in bytes:
        integer *= 256
        # this used to be StringType which includes unicode, however, this
        # loop doesn't correctly handle unicode data, so the change should also
        # be a bug fix
        if type(byte) is str: byte = ord(byte)
        integer += byte

    return integer

def rsa_int2bytes(number):
    """Converts a number to a string of bytes
    
    >>> bytes2int(int2bytes(123456789))
    123456789
    """

    if not (type(number) is long or type(number) is int):
        raise TypeError("You must pass a long or an int")

    string = ""

    while number > 0:
        string = "%s%s" % (chr(number & 0xFF), string)
        number /= 256
    
    if string[0] != '\001':
        raise TypeError("Invalid RSA data")
 
    return string[1:]

def rsa_fast_exponentiation(a, p, n):
    """Calculates r = a^p mod n
    """
    result = a % n
    remainders = []
    while p != 1:
        remainders.append(p & 1)
        p = p >> 1
    while remainders:
        rem = remainders.pop()
        result = ((a ** rem) * result ** 2) % n
    return result

def rsa_fermat_little_theorem(p):
    """Returns 1 if p may be prime, and something else if p definitely
    is not prime"""

    a = random_randint(1, p-1)
    return rsa_fast_exponentiation(a, p-1, p)

def rsa_jacobi(a, b):
    """Calculates the value of the Jacobi symbol (a/b)
    """

    if a % b == 0:
        return 0
    result = 1
    while a > 1:
        if a & 1:
            if ((a-1)*(b-1) >> 2) & 1:
                result = -result
            b, a = a, b % a
        else:
            if ((b ** 2 - 1) >> 3) & 1:
                result = -result
            a = a >> 1
    return result

def rsa_jacobi_witness(x, n):
    """Returns False if n is an Euler pseudo-prime with base x, and
    True otherwise.
    """

    j = rsa_jacobi(x, n) % n
    f = rsa_fast_exponentiation(x, (n-1)/2, n)

    if j == f: return False
    return True

def rsa_randomized_primality_testing(n, k):
    """Calculates whether n is composite (which is always correct) or
    prime (which is incorrect with error probability 2**-k)

    Returns False if the number if composite, and True if it's
    probably prime.
    """

    q = 0.5     # Property of the jacobi_witness function

    t = int(math_ceil(k / math_log(1/q, 2)))
    for junk in range(t+1):
        # JAC: Sometimes we get a ValueError here because the range is empty 
        # (i.e. we are doing randint(1,1) or randint (1,0), etc.).   I'll check
        # and return False in this case and declare 1 and 2 composite (since 
        # they make horrible p or q in RSA).
        if n-1 < 2:
          return False
        x = random_randint(1, n-1)
        if rsa_jacobi_witness(x, n): return False
    
    return True

def rsa_is_prime(number):
    """Returns True if the number is prime, and False otherwise.

    >>> rsa_is_prime(42)
    0
    >>> rsa_is_prime(41)
    1
    """

    """
    if not fermat_little_theorem(number) == 1:
        # Not prime, according to Fermat's little theorem
        return False
    """

    if rsa_randomized_primality_testing(number, 5):
        # Prime, according to Jacobi
        return True
    
    # Not prime
    return False

    
def rsa_getprime(nbits):
    """Returns a prime number of max. 'math_ceil(nbits/8)*8' bits. In
    other words: nbits is rounded up to whole bytes.

    >>> p = getprime(8)
    >>> rsa_is_prime(p-1)
    0
    >>> rsa_is_prime(p)
    1
    >>> rsa_is_prime(p+1)
    0
    """

    while True:
#        integer = read_random_int(nbits)
        integer = random_randint(1,2**nbits)

        # Make sure it's odd
        integer |= 1

        # Test for primeness
        if rsa_is_prime(integer): break

        # Retry if not prime

    return integer

def rsa_are_relatively_prime(a, b):
    """Returns True if a and b are relatively prime, and False if they
    are not.

    >>> are_relatively_prime(2, 3)
    1
    >>> are_relatively_prime(2, 4)
    0
    """

    d = rsa_gcd(a, b)
    return (d == 1)

def rsa_find_p_q(nbits):
    """Returns a tuple of two different primes of nbits bits"""

    p = rsa_getprime(nbits)
    while True:
        q = rsa_getprime(nbits)
        if not q == p: break
    
    return (p, q)

def rsa_extended_euclid_gcd(a, b):
    """Returns a tuple (d, i, j) such that d = gcd(a, b) = ia + jb
    """

    if b == 0:
        return (a, 1, 0)

    q = abs(a % b)
    r = long(a / b)
    (d, k, l) = rsa_extended_euclid_gcd(b, q)

    return (d, l, k - l*r)

# Main function: calculate encryption and decryption keys
def rsa_calculate_keys(p, q, nbits):
    """Calculates an encryption and a decryption key for p and q, and
    returns them as a tuple (e, d)"""

    n = p * q
    phi_n = (p-1) * (q-1)

    while True:
        # Make sure e has enough bits so we ensure "wrapping" through
        # modulo n
        e = rsa_getprime(max(8, nbits/2))
        if rsa_are_relatively_prime(e, n) and rsa_are_relatively_prime(e, phi_n): break

    (d, i, j) = rsa_extended_euclid_gcd(e, phi_n)

    if not d == 1:
        raise Exception("e (%d) and phi_n (%d) are not relatively prime" % (e, phi_n))

    if not (e * i) % phi_n == 1:
        raise Exception("e (%d) and i (%d) are not mult. inv. modulo phi_n (%d)" % (e, i, phi_n))

    return (e, i)


def rsa_gen_keys(nbits):
    """Generate RSA keys of nbits bits. Returns (p, q, e, d).
    """

    while True:
        (p, q) = rsa_find_p_q(nbits)
        (e, d) = rsa_calculate_keys(p, q, nbits)

        # For some reason, d is sometimes negative. We don't know how
        # to fix it (yet), so we keep trying until everything is shiny
        if d > 0: break

    return (p, q, e, d)

def rsa_gen_pubpriv_keys(nbits):
    """Generates public and private keys, and returns them as (pub,
    priv).

    The public key consists of a dict {e: ..., , n: ....). The private
    key consists of a dict {d: ...., p: ...., q: ....).
    """
    
    (p, q, e, d) = rsa_gen_keys(nbits)

    return ( {'e': e, 'n': p*q}, {'d': d, 'p': p, 'q': q} )


def rsa_encrypt_int(message, ekey, n):
    """Encrypts a message using encryption key 'ekey', working modulo
    n"""

    if type(message) is int:
        return rsa_encrypt_int(long(message), ekey, n)

    if not type(message) is long:
        raise TypeError("You must pass a long or an int")

    if math_floor(math_log(message, 2)) > math_floor(math_log(n, 2)):
        raise OverflowError("The message is too long")

    return rsa_fast_exponentiation(message, ekey, n)

def rsa_decrypt_int(cyphertext, dkey, n):
    """Decrypts a cypher text using the decryption key 'dkey', working
    modulo n"""

    return rsa_encrypt_int(cyphertext, dkey, n)

def rsa_sign_int(message, dkey, n):
    """Signs 'message' using key 'dkey', working modulo n"""

    return rsa_decrypt_int(message, dkey, n)

def rsa_verify_int(signed, ekey, n):
    """verifies 'signed' using key 'ekey', working modulo n"""

    return rsa_encrypt_int(signed, ekey, n)

def rsa_picklechops(chops):
    """previously used to pickles and base64encodes it's argument chops"""

    retstring = ''
    for item in chops:
      retstring = retstring + ' ' + str(item)
    return retstring

def rsa_unpicklechops(string):
    """previously used to base64decode and unpickle it's argument string"""

    retchops = []
    for item in string.split():
      retchops.append(long(item))
    return retchops

def rsa_chopstring(message, key, n, funcref):
    """Splits 'message' into chops that are at most as long as n,
    converts these into integers, and calls funcref(integer, key, n)
    for each chop.

    Used by 'encrypt' and 'sign'.
    """

    msglen = len(message)
    nbits = int(math_floor(math_log(n, 2)))
    # JAC: subtract a byte because we're going to add an extra char on the front
    # to properly handle leading \000 bytes
    nbytes = int(nbits / 8)-1
    blocks = int(msglen / nbytes)

    if msglen % nbytes > 0:
        blocks += 1

    cypher = []
    
    for bindex in range(blocks):
        offset = bindex * nbytes
        block = message[offset:offset+nbytes]
        value = rsa_bytes2int(block)
        cypher.append(funcref(value, key, n))

    return rsa_picklechops(cypher)

def rsa_gluechops(chops, key, n, funcref):
    """Glues chops back together into a string.  calls
    funcref(integer, key, n) for each chop.

    Used by 'decrypt' and 'verify'.
    """
    message = ""

    chops = rsa_unpicklechops(chops)
    
    for cpart in chops:
        mpart = funcref(cpart, key, n)
        message += rsa_int2bytes(mpart)
    
    return message

def rsa_encrypt(message, key):
    """Encrypts a string 'message' with the public key 'key'"""
    
    return rsa_chopstring(message, key['e'], key['n'], rsa_encrypt_int)

def rsa_sign(message, key):
    """Signs a string 'message' with the private key 'key'"""
    
    return rsa_chopstring(message, key['d'], key['p']*key['q'], rsa_decrypt_int)

def rsa_decrypt(cypher, key):
    """Decrypts a cypher with the private key 'key'"""

    return rsa_gluechops(cypher, key['d'], key['p']*key['q'], rsa_decrypt_int)

def rsa_verify(cypher, key):
    """Verifies a cypher with the public key 'key'"""

    return rsa_gluechops(cypher, key['e'], key['n'], rsa_encrypt_int)


def rsa_is_valid_privatekey(key):
    """This tries to determine if a key is valid.   If it returns False, the
       key is definitely invalid.   If True, the key is almost certainly valid"""
    # must be a dict
    if type(key) is not dict:
        return False

    # missing the right keys
    if 'd' not in key or 'p' not in key or 'q' not in key:
        return False

    # has extra data in the key
    if len(key) != 3:
        return False

    for item in ['d', 'p', 'q']:
        # must have integer or long types for the key components...
        if type(key[item]) is not int and type(key[item]) is not long:
            return False

    if rsa_is_prime(key['p']) and rsa_is_prime(key['q']):
        # Seems valid...
        return True
    else:
        return False
  

def rsa_is_valid_publickey(key):
    """This tries to determine if a key is valid.   If it returns False, the
       key is definitely invalid.   If True, the key is almost certainly valid"""
    # must be a dict
    if type(key) is not dict:
        return False

    # missing the right keys
    if 'e' not in key or 'n' not in key:
        return False

    # has extra data in the key
    if len(key) != 2:
        return False

    for item in ['e', 'n']:
        # must have integer or long types for the key components...
        if type(key[item]) is not int and type(key[item]) is not long:
            return False

    if key['e'] < key['n']:
        # Seems valid...
        return True
    else:
        return False
  

def rsa_publickey_to_string(key):
  if not rsa_is_valid_publickey(key):
    raise ValueError, "Invalid public key"

  return str(key['e'])+" "+str(key['n'])


def rsa_string_to_publickey(mystr):
  if len(mystr.split()) != 2:
    raise ValueError, "Invalid public key string"

  
  return {'e':long(mystr.split()[0]), 'n':long(mystr.split()[1])}



def rsa_privatekey_to_string(key):
  if not rsa_is_valid_privatekey(key):
    raise ValueError, "Invalid private key"

  return str(key['d'])+" "+str(key['p'])+" "+str(key['q'])


def rsa_string_to_privatekey(mystr):
  if len(mystr.split()) != 3:
    raise ValueError, "Invalid private key string"

  
  return {'d':long(mystr.split()[0]), 'p':long(mystr.split()[1]), 'q':long(mystr.split()[2])}


def rsa_privatekey_to_file(key,filename):
  if not rsa_is_valid_privatekey(key):
    raise ValueError, "Invalid private key"

  fileobject = file(filename,"w")
  fileobject.write(rsa_privatekey_to_string(key))
  fileobject.close()



def rsa_file_to_privatekey(filename):
  fileobject = file(filename,'r')
  privatekeystring = fileobject.read()
  fileobject.close()

  return rsa_string_to_privatekey(privatekeystring)



def rsa_publickey_to_file(key,filename):
  if not rsa_is_valid_publickey(key):
    raise ValueError, "Invalid public key"

  fileobject = file(filename,"w")
  fileobject.write(rsa_publickey_to_string(key))
  fileobject.close()



def rsa_file_to_publickey(filename):
  fileobject = file(filename,'r')
  publickeystring = fileobject.read()
  fileobject.close()

  return rsa_string_to_publickey(publickeystring)


def rsa_matching_keys(privatekey, publickey):
  """
  <Purpose>
    Determines if a pair of public and private keys match and allow for encryption/decryption.
  
  <Arguments>
    privatekey: The private key*
    publickey:  The public key*
    
    * The dictionary structure, not the string or file name
  <Returns>
    True, if they can be used. False otherwise.
  """
  # We will attempt to encrypt then decrypt and check that the message matches
  testmessage = "A quick brown fox."
  
  # Encrypt with the public key
  encryptedmessage = rsa_encrypt(testmessage, publickey)

  # Decrypt with the private key
  try:
    decryptedmessage = rsa_decrypt(encryptedmessage, privatekey)
  except TypeError:
    # If there was an exception, assume the keys are to blame
    return False
  except OverflowError:
    # There was an overflow while decrypting, blame the keys
    return False  
  
  # Test for a match
  return (testmessage == decryptedmessage)


#end include rsa.repy

###Constants###

#file containing information on update and query servers and their public keys
UPDATE_SERVER_FILE="update_query_server_list.txt"

#file containing information on registration servers and their public keys
REGISTRATION_SERVER_FILE = "registration_server_list.txt"


#used to get a dict associating server addresses with public keys
def cncFileParser_read_server_list_file(filename):
  #each line in the file is of the format: <ip>:<port> <publickey>,
  #where the public key string uses '#' as separators internally instead of the 'space' character
  #return a dict where each key is a string of the form <ip>:<port> and each entry is the public key of that server (key is of type dict)
  result_dict = dict()

  f = open(filename)
  for line in f:
      tokenlist = line.split()
      if (len(tokenlist)>1):
        
        #try statement so thta if there is an error in one entry, we can continue
        try:
          space_separated_key = tokenlist[1].replace('#',' ')
          result_dict[tokenlist[0]] = rsa_string_to_publickey(space_separated_key)
        except KeyError, e:
          print "error in building server-public_key dict: " + str(e)
  f.close()
  
  return result_dict
#end include cncFileParser.repy
#begin include random.repy
#already included random.repy
#end include random.repy
#begin include keyrangelib.repy
"""
<Author>
  Cosmin Barsan
  
<Purpose>
  Library that provides utility and helper functions for key range related tasks
"""

#begin include sha.repy
#!/usr/bin/env python
# -*- coding: iso-8859-1

"""A sample implementation of SHA-1 in pure Python.

   Adapted by Justin Cappos from the version at: http://codespeak.net/pypy/dist/pypy/lib/sha.py

   Framework adapted from Dinu Gherman's MD5 implementation by
   J. Hall`en and L. Creighton. SHA-1 implementation based directly on
   the text of the NIST standard FIPS PUB 180-1.

date    = '2004-11-17'
version = 0.91 # Modernised by J. Hall`en and L. Creighton for Pypy
"""



# ======================================================================
# Bit-Manipulation helpers
#
#   _long2bytes() was contributed by Barry Warsaw
#   and is reused here with tiny modifications.
# ======================================================================

def _sha_long2bytesBigEndian(n, thisblocksize=0):
    """Convert a long integer to a byte string.

    If optional blocksize is given and greater than zero, pad the front
    of the byte string with binary zeros so that the length is a multiple
    of blocksize.
    """

    # Justin: I changed this to avoid using pack. I didn't test performance, etc
    s = ''
    while n > 0:
        #original: 
        # s = struct.pack('>I', n & 0xffffffffL) + s
        # n = n >> 32
        s = chr(n & 0xff) + s
        n = n >> 8

    # Strip off leading zeros.
    for i in range(len(s)):
        if s[i] <> '\000':
            break
    else:
        # Only happens when n == 0.
        s = '\000'
        i = 0

    s = s[i:]

    # Add back some pad bytes. This could be done more efficiently
    # w.r.t. the de-padding being done above, but sigh...
    if thisblocksize > 0 and len(s) % thisblocksize:
        s = (thisblocksize - len(s) % thisblocksize) * '\000' + s

    return s


def _sha_bytelist2longBigEndian(list):
    "Transform a list of characters into a list of longs."

    imax = len(list)/4
    hl = [0L] * imax

    j = 0
    i = 0
    while i < imax:
        b0 = long(ord(list[j])) << 24
        b1 = long(ord(list[j+1])) << 16
        b2 = long(ord(list[j+2])) << 8
        b3 = long(ord(list[j+3]))
        hl[i] = b0 | b1 | b2 | b3
        i = i+1
        j = j+4

    return hl


def _sha_rotateLeft(x, n):
    "Rotate x (32 bit) left n bits circularly."

    return (x << n) | (x >> (32-n))


# ======================================================================
# The SHA transformation functions
#
# ======================================================================

# Constants to be used
sha_K = [
    0x5A827999L, # ( 0 <= t <= 19)
    0x6ED9EBA1L, # (20 <= t <= 39)
    0x8F1BBCDCL, # (40 <= t <= 59)
    0xCA62C1D6L  # (60 <= t <= 79)
    ]

class sha:
    "An implementation of the MD5 hash function in pure Python."

    def __init__(self):
        "Initialisation."
        
        # Initial message length in bits(!).
        self.length = 0L
        self.count = [0, 0]

        # Initial empty message as a sequence of bytes (8 bit characters).
        self.inputdata = []

        # Call a separate init function, that can be used repeatedly
        # to start from scratch on the same object.
        self.init()


    def init(self):
        "Initialize the message-digest and set all fields to zero."

        self.length = 0L
        self.inputdata = []

        # Initial 160 bit message digest (5 times 32 bit).
        self.H0 = 0x67452301L
        self.H1 = 0xEFCDAB89L
        self.H2 = 0x98BADCFEL
        self.H3 = 0x10325476L
        self.H4 = 0xC3D2E1F0L

    def _transform(self, W):

        for t in range(16, 80):
            W.append(_sha_rotateLeft(
                W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1) & 0xffffffffL)

        A = self.H0
        B = self.H1
        C = self.H2
        D = self.H3
        E = self.H4

        """
        This loop was unrolled to gain about 10% in speed
        for t in range(0, 80):
            TEMP = _sha_rotateLeft(A, 5) + sha_f[t/20] + E + W[t] + sha_K[t/20]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL
        """

        for t in range(0, 20):
            TEMP = _sha_rotateLeft(A, 5) + ((B & C) | ((~ B) & D)) + E + W[t] + sha_K[0]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(20, 40):
            TEMP = _sha_rotateLeft(A, 5) + (B ^ C ^ D) + E + W[t] + sha_K[1]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(40, 60):
            TEMP = _sha_rotateLeft(A, 5) + ((B & C) | (B & D) | (C & D)) + E + W[t] + sha_K[2]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(60, 80):
            TEMP = _sha_rotateLeft(A, 5) + (B ^ C ^ D)  + E + W[t] + sha_K[3]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL


        self.H0 = (self.H0 + A) & 0xffffffffL
        self.H1 = (self.H1 + B) & 0xffffffffL
        self.H2 = (self.H2 + C) & 0xffffffffL
        self.H3 = (self.H3 + D) & 0xffffffffL
        self.H4 = (self.H4 + E) & 0xffffffffL
    

    # Down from here all methods follow the Python Standard Library
    # API of the sha module.

    def update(self, inBuf):
        """Add to the current message.

        Update the md5 object with the string arg. Repeated calls
        are equivalent to a single call with the concatenation of all
        the arguments, i.e. m.update(a); m.update(b) is equivalent
        to m.update(a+b).

        The hash is immediately calculated for all full blocks. The final
        calculation is made in digest(). It will calculate 1-2 blocks,
        depending on how much padding we have to add. This allows us to
        keep an intermediate value for the hash, so that we only need to
        make minimal recalculation if we call update() to add more data
        to the hashed string.
        """

        leninBuf = long(len(inBuf))

        # Compute number of bytes mod 64.
        index = (self.count[1] >> 3) & 0x3FL

        # Update number of bits.
        self.count[1] = self.count[1] + (leninBuf << 3)
        if self.count[1] < (leninBuf << 3):
            self.count[0] = self.count[0] + 1
        self.count[0] = self.count[0] + (leninBuf >> 29)

        partLen = 64 - index

        if leninBuf >= partLen:
            self.inputdata[index:] = list(inBuf[:partLen])
            self._transform(_sha_bytelist2longBigEndian(self.inputdata))
            i = partLen
            while i + 63 < leninBuf:
                self._transform(_sha_bytelist2longBigEndian(list(inBuf[i:i+64])))
                i = i + 64
            else:
                self.inputdata = list(inBuf[i:leninBuf])
        else:
            i = 0
            self.inputdata = self.inputdata + list(inBuf)


    def digest(self):
        """Terminate the message-digest computation and return digest.

        Return the digest of the strings passed to the update()
        method so far. This is a 16-byte string which may contain
        non-ASCII characters, including null bytes.
        """

        H0 = self.H0
        H1 = self.H1
        H2 = self.H2
        H3 = self.H3
        H4 = self.H4
        inputdata = [] + self.inputdata
        count = [] + self.count

        index = (self.count[1] >> 3) & 0x3fL

        if index < 56:
            padLen = 56 - index
        else:
            padLen = 120 - index

        padding = ['\200'] + ['\000'] * 63
        self.update(padding[:padLen])

        # Append length (before padding).
        bits = _sha_bytelist2longBigEndian(self.inputdata[:56]) + count

        self._transform(bits)

        # Store state in digest.
        digest = _sha_long2bytesBigEndian(self.H0, 4) + \
                 _sha_long2bytesBigEndian(self.H1, 4) + \
                 _sha_long2bytesBigEndian(self.H2, 4) + \
                 _sha_long2bytesBigEndian(self.H3, 4) + \
                 _sha_long2bytesBigEndian(self.H4, 4)

        self.H0 = H0 
        self.H1 = H1 
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4
        self.inputdata = inputdata 
        self.count = count 

        return digest


    def hexdigest(self):
        """Terminate and return digest in HEX form.

        Like digest() except the digest is returned as a string of
        length 32, containing only hexadecimal digits. This may be
        used to exchange the value safely in email or other non-
        binary environments.
        """
        return ''.join(['%02x' % ord(c) for c in self.digest()])

    def copy(self):
        """Return a clone object. (not implemented)

        Return a copy ('clone') of the md5 object. This can be used
        to efficiently compute the digests of strings that share
        a common initial substring.
        """
        raise Exception, "not implemented"


# ======================================================================
# Mimic Python top-level functions from standard library API
# for consistency with the md5 module of the standard library.
# ======================================================================

# These are mandatory variables in the module. They have constant values
# in the SHA standard.

sha_digest_size = sha_digestsize = 20
sha_blocksize = 1

def sha_new(arg=None):
    """Return a new sha crypto object.

    If arg is present, the method call update(arg) is made.
    """

    crypto = sha()
    if arg:
        crypto.update(arg)

    return crypto


# gives the hash of a string
def sha_hash(string):
    crypto = sha()
    crypto.update(string)
    return crypto.digest()


# gives the hash of a string
def sha_hexhash(string):
    crypto = sha()
    crypto.update(string)
    return crypto.hexdigest()

#end include sha.repy


#this constant defines how many digits (0-9) the userkey range must cover.
#for instance, if the UPDATE_SERVER_KEYRANGE_SPACE variable is set to 3, hashes of user keys will take values between 0 and 999
UPDATE_SERVER_KEYRANGE_SPACE = 3 

#converts a given public key to a cnc userkey that is compatible with the cnc system.
def keyrangelib_publickey_to_cncuserkey(publickey):
  string_key = rsa_publickey_to_string(publickey)
  
  #hash the string
  hashed_key = sha_hexhash(string_key)
  
  #remove spaces
  resultkey = hashed_key.replace(' ','#')
  
  return resultkey
  
#gets a hash of the specified length for a given string. Used to determine which range a user key falls into
def keyrangelib_get_short_hash(arg_string, num_digits = UPDATE_SERVER_KEYRANGE_SPACE):
  long_hex_result = sha_hexhash(arg_string)
  long_int_result = int(long_hex_result, 16)
  short_result = long_int_result%(10**num_digits)
  return short_result
  
  
#for a specified user key, returns a list of update servers or query servers whose key ranges cover the key. returns list of ip,port pairs
#update_key_range_table and query_server_table must be given as parameters
def keyrangelib_get_addresses_for_userkey(userkey, update_key_range_table, query_server_table):
  
  #we will add matching addresses to this list
  result_address_list = []
  
  #first check the query_server_table
  if userkey in query_server_table.keys(): 
    #the userkey is in the query server table, meaning it will not be in the update_key_range_table
    #return the list of addresses from the query server table
    return query_server_table[userkey]


  #get the hash of the key to check if there are mathcing update servers.
  key_hash = keyrangelib_get_short_hash(userkey)
  
  #for every key range, we check if the hash value is within the range
  for keyrange in update_key_range_table.keys() :
    #if there are no entries under this key range skip it
    if len(update_key_range_table[keyrange])==0:
      continue
      
    lower_bound, upper_bound = keyrange
    
    #check if the key hash falls into the range
    if (lower_bound <= key_hash and key_hash<=upper_bound):
      result_address_list.extend(update_key_range_table[keyrange])
  
  return result_address_list
  
  
#parses the string representation of a update key range dict and returns it in dict form
def keyrangelib_parse_update_key_ranges_string(keyrangestring):

  #structure that indicates the update servers with each key range
  #each key is a pair of integers (lower user key, upper user key). Each entry is a list of (ip, port) pairs giving the address of the servers in the respective update unit. 
  update_key_range_table = dict()
  
  #if there are no entries, return empty dict
  if keyrangestring=="None" :
    return update_key_range_table
  
  #split the string to a list of entries
  entries = keyrangestring.split(';')
  
  for entry in entries:
    range_str,addresses_str = entry.split(':')
    lowerboundstr,upperboundstr = range_str.split(',')
    range_value = (int(lowerboundstr), int(upperboundstr))
    
    address_str_list=addresses_str.split('%')
    address_result_list = []
    for address_str in address_str_list:
      ip,port_str = address_str.split(',')
      port = int(port_str)
      address = ip,port
      
      #append the address to the result list for the current entry
      address_result_list.append(address)
      
    #add the entry to the dict
    update_key_range_table[range_value] = address_result_list
    
  return update_key_range_table
  
#parses the string representation of a query table and returns it in dict form
def keyrangelib_parse_query_table_string(querytablestring):

  #structure that keeps track of which query servers correspond to a given userkey
  #each key is a userkey of type string. Each entry is a list of (ip, port) pairs giving the address of the servers in the query unit for the particular userkey. 
  query_server_table = dict()
  
  #if there are no entries, return empty dict
  if querytablestring=="None" :
    return query_server_table
  
  #split the string to a list of entries
  entries = querytablestring.split(';')
  
  for entry in entries:
    userkey,addresses_str = entry.split(':')
    
    address_str_list=addresses_str.split('%')
    address_result_list = []
    for address_str in address_str_list:
      ip,port_str = address_str.split(',')
      port = int(port_str)
      address = ip,port
      
      #append the address to the result list for the current entry
      address_result_list.append(address)
      
    #add the entry to the dict
    query_server_table[userkey] = address_result_list
    
  return query_server_table
#end include keyrangelib.repy
#begin include cncSignData.repy
"""
<Library Name>
  cncSignData.repy

<Started>
  March 31, 2009

<Author>
  Cosmin Barsan
  
<Purpose>
  Similar to signeddata.repy, but it is simpler and easier to use with cnc packets. Most of the code was taken from the signeddata.repy file.

"""
#begin include signeddata.repy
""" Justin Cappos -- routines that create and verify signatures and prevent
replay / freeze / out of sequence / misdelivery attacks

Replay attack:   When someone provides information you signed before to try
to get you to perform an old action again.   For example, A sends messages to
the node manager to provide a vessel to B (B intercepts this traffic).   Later 
A acquires the vessel again.   B should not be able to replay the messages A 
sent to the node manager to have the vessel transferred to B again.

Freeze attack:   When an attacker can act as a man-in-the-middle and provide
stale information to an attacker.   For example, B can intercept all traffic
between the node manager and A.   If C makes a change on the node manager, then
B should not be able to prevent A from seeing the change (at least within 
some time bound).

Out of sequence attack:   When someone can skip sending some messages but
deliver others.   For example, A wants to stop the current program, upload
a new copy of the program, and start the program again.   It should be possible
for A to specify that these actions must be performed in order and without 
skipping any of the prior actions (regardless of failures, etc.).

Misdelivery attack:   Messages should only be acted upon by the nodes that 
the user intended.   A malicious party should not be able to "misdeliver" a
message and have a different node perform the action.



I have support for "sequence numbers" which will require that intermediate 
events are not skipped.    The sequence numbers are a tuple: (tag, version)

"""


#begin include sha.repy
#already included sha.repy
#end include sha.repy
#begin include rsa.repy
#already included rsa.repy
#end include rsa.repy
#begin include time.repy
#already included time.repy
#end include time.repy


# The signature for a piece of data is appended to the end and has the format:
# \n!publickey!timestamp!expirationtime!sequencedata!destination!signature
# The signature is actually the sha hash of the data (including the
# publickey, timestamp, expirationtime, sequencedata and destination) encrypted
# by the private key.



# I'll allow None and any int, long, or float (can be 0 or negative)
def signeddata_is_valid_timestamp(timestamp):
  if timestamp == None:
    return True

  if type(timestamp) is not int and type(timestamp) is not long and type(timestamp) is not float:
    return False

  return True

  
# I'll allow None and any int, long, or float that is 0 or positive
def signeddata_is_valid_expirationtime(expirationtime):
  if expirationtime == None:
    return True

  if type(expirationtime) is not int and type(expirationtime) is not long and type(expirationtime) is not float:
    return False

  if expirationtime < 0:
    return False

  return True





# sequence numbers must be 'tag:num' where tag doesn't contain ':','\n', or '!' # and num is a number
def signeddata_is_valid_sequencenumber(sequencenumber):
  if sequencenumber == None:
    return True

  if type(sequencenumber) != tuple:
    return False

  if len(sequencenumber) != 2:
    return False

  if type(sequencenumber[0]) != str:
    return False
  
  if '!' in sequencenumber[0] or ':' in sequencenumber[0] or '\n' in sequencenumber[0]:
    return False

  if type(sequencenumber[1]) != long and type(sequencenumber[1]) != int:
    return False

  return True

# Destination is an "opaque string" or None.  Should not contain a '!' or '\n'
def signeddata_is_valid_destination(destination):
  if type(destination) == type(None):
    return True

  # a string without '!' or '\n' ('!' is the separator character, '\n' is not
  # allowed anywhere in the signature)
  if type(destination) == type('abc') and '!' not in destination and '\n' not in destination:
    return True

  return False
  


#applies a signature to a given message (parameter data) and returns the signed message
def signeddata_signdata(data, privatekey, publickey, timestamp=None, expiration=None, sequenceno=None,destination=None):

  if not signeddata_is_valid_timestamp(timestamp):
    raise ValueError, "Invalid Timestamp"

  if not signeddata_is_valid_expirationtime(expiration):
    raise ValueError, "Invalid Expiration Time"

  if not signeddata_is_valid_sequencenumber(sequenceno):
    raise ValueError, "Invalid Sequence Number"

  if not signeddata_is_valid_destination(destination):
    raise ValueError, "Invalid Destination"


  # Build up \n!pubkey!timestamp!expire!sequence!dest!signature
  totaldata = data + "\n!"+rsa_publickey_to_string(publickey)
  totaldata = totaldata+"!"+signeddata_timestamp_to_string(timestamp)
  totaldata = totaldata+"!"+signeddata_expiration_to_string(expiration)
  totaldata = totaldata+"!"+signeddata_sequencenumber_to_string(sequenceno)
  totaldata = totaldata+"!"+signeddata_destination_to_string(destination)
  
  #generate the signature
  signature = signeddata_create_signature(totaldata, privatekey, publickey)
  
  totaldata = totaldata+"!"+ signature

  return totaldata

#creates a signature for the given data string and returns it
def signeddata_create_signature(data, privatekey, publickey):

  # NOTE: This takes waaaay too long.   I'm going to do something simpler...
  #  if not rsa_is_valid_privatekey(privatekey):
  #    raise ValueError, "Invalid Private Key"
  if not privatekey:
    raise ValueError, "Invalid Private Key"
      
  if not rsa_is_valid_publickey(publickey):
    raise ValueError, "Invalid Public Key"
    
  # Time to get the hash...
  shahashobj = sha()
  shahashobj.update(data)
  hashdata = shahashobj.digest()


  # ...and sign it
  signature = rsa_sign(hashdata, privatekey)
  
  return str(signature)


# return [original data, signature]
def signeddata_split_signature(data):
  return data.rsplit('\n',1)


# checks the signature.   If the public key is specified it must match that in
# the file...
def signeddata_issignedcorrectly(data, publickey=None):
  # I'll check signature over all of thesigneddata
  thesigneddata, signature = data.rsplit('!',1)
  junk, rawpublickey, junktimestamp, junkexpiration, junksequenceno, junkdestination = thesigneddata.rsplit('!',5)
  
  if publickey != None and rsa_string_to_publickey(rawpublickey) != publickey:
    return False

  publickey = rsa_string_to_publickey(rawpublickey)

  try: 
    # extract the hash from the signature
    signedhash = rsa_verify(signature, publickey)
  except TypeError, e:
    if 'RSA' not in str(e):
      raise
    # Bad signature or public key
    return False
  except OverflowError, e:      
    #bad signature 
    #this is most likely caused by mismatched public and private keys.
    return False
    
  # Does the hash match the signed data?
  if signedhash == sha_hash(thesigneddata):
    return True
  else:
    return False
  

def signeddata_string_to_destination(destination):
  if destination == 'None':
    return None
  return destination

def signeddata_destination_to_string(destination):
  return str(destination)


def signeddata_string_to_timestamp(rawtimestamp):
  if rawtimestamp == 'None':
    return None
  return float(rawtimestamp)


def signeddata_timestamp_to_string(timestamp):
  return str(timestamp)

def signeddata_string_to_expiration(rawexpiration):
  if rawexpiration == 'None':
    return None
  return float(rawexpiration)

def signeddata_expiration_to_string(expiration):
  return str(expiration)



def signeddata_string_to_sequencenumber(sequencenumberstr):
  if sequencenumberstr == 'None' or sequencenumberstr == None:
    return None

  if type(sequencenumberstr) is not str:
    raise ValueError, "Invalid sequence number type '"+str(type(sequencenumberstr))+"' (must be string)"
    
  if len(sequencenumberstr.split(':')) != 2:
    raise ValueError, "Invalid sequence number string (does not contain 1 ':')"

  if '!' in sequencenumberstr:
    raise ValueError, "Invalid sequence number data: '!' not allowed"
  
  return sequencenumberstr.split(':')[0],int(sequencenumberstr.split(':')[1])


def signeddata_sequencenumber_to_string(sequencenumber):
  if type(sequencenumber) is type(None):
    return 'None'

  if type(sequencenumber[0]) is not str:
    raise ValueError, "Invalid sequence number type"

  if type(sequencenumber[1]) is not long and type(sequencenumber[1]) is not int:
    raise ValueError, "Invalid sequence number count type"
    
  if len(sequencenumber) != 2:
    raise ValueError, "Invalid sequence number"

  return sequencenumber[0]+":"+str(sequencenumber[1])


def signeddata_iscurrent(expiretime):
  if expiretime == None:
    return True

  # may throw TimeError...
  currenttime = time_gettime()
  if expiretime > currenttime:
    return True
  else:
    return False




def signeddata_has_good_sequence_transition(oldsequence, newsequence):
  # None is always allowed by any prior sequence
  if newsequence == None:
    return True
    
  #newsequence is a tuple
  newsequencename,st_newsequenceno = newsequence
  newsequenceno = int(st_newsequenceno)

  if oldsequence == None: 
    # is this the start of a sequence when there was none prior?
    if newsequenceno == 0:
      return True
    return False
  
  # oldsequence is a pair.
  oldsequencename,st_oldsequenceno = oldsequence
  oldsequenceno = int(st_oldsequenceno)
  

  
  # They are from the same sequence
  if oldsequencename == newsequencename:
    # and this must be the next number to be valid
    if oldsequenceno + 1 == newsequenceno:
      return True
    return False

  else: 
    # Different sequences
 
    # is this the start of a new sequence?
    if newsequenceno == 0:
      return True

    # otherwise this isn't good
    return False


# used in lieu of a global for destination checking
signeddata_identity = {}

# Used to set identity for destination checking...
def signeddata_set_identity(identity):
  signeddata_identity['me'] = identity


def signeddata_destined_for_me(destination):
  # None means it's for everyone
  if destination == None:
    return True

  # My identity wasn't set and the destination was, so fail...
  if 'me' not in signeddata_identity:
    return False

  # otherwise, am I in the colon delimited list?
  if signeddata_identity['me'] in destination.split(':'):
    return True
  return False



def signeddata_split(data):
  originaldata, rawpublickey, rawtimestamp, rawexpiration, rawsequenceno,rawdestination, junksignature = data.rsplit('!',6)
  
  # strip the '\n' off of the original data...
  return originaldata[:-1], rsa_string_to_publickey(rawpublickey), signeddata_string_to_timestamp(rawtimestamp), signeddata_string_to_expiration(rawexpiration), signeddata_string_to_sequencenumber(rawsequenceno), signeddata_string_to_destination(rawdestination)



def signeddata_getcomments(signeddata, publickey=None):
  """Returns a list of problems with the signed data (but doesn't look at sequence number or timestamp data)."""
  returned_comments = []

  try:
    junkdata, pubkey, timestamp, expiretime, sequenceno, destination = signeddata_split(signeddata)
  except KeyError:
    return ['Malformed signed data']

  if publickey != None and publickey != pubkey:
    returned_comments.append('Different public key')

  if not signeddata_issignedcorrectly(signeddata, publickey):
    returned_comments.append("Bad signature")
  
  try:
    if not signeddata_iscurrent(expiretime):
      returned_comments.append("Expired signature")
  except TimeError:
    returned_comments.append("Cannot check expiration")

  #BUG FIX: destination checking has been re-enabled since teh issue with identities not being stored correctly has been fixed
  if destination != None and not signeddata_destined_for_me(destination):
    returned_comments.append("Not destined for this node")


  return returned_comments



signeddata_warning_comments = [ 'Timestamps match', "Cannot check expiration" ]
signeddata_fatal_comments = ['Malformed signed data', 'Different public key', "Bad signature", "Expired signature", 'Public keys do not match', 'Invalid sequence transition', 'Timestamps out of order', 'Not destined for this node']

signeddata_all_comments = signeddata_warning_comments + signeddata_fatal_comments

def signeddata_shouldtrustmeta(oldsignature, newsigneddata, publickey=None):
  """
  the signature of the metadata should be specified for the oldsignature parameter
  newsigneddata must contain the full request,
  """
  return signeddata_shouldtrust(oldsignature, newsigneddata, publickey=None, oldsigneddata_is_fullrequest=False)

def signeddata_shouldtrust(oldsigneddata, newsigneddata, publickey=None, oldsigneddata_is_fullrequest=True):
  """ Returns False for 'don't trust', None for 'use your discretion' and True 
  for everything is okay.   The second item in the return value is a list of
  reasons / justifications
  newsigneddata must contain full request
  by default, oldsigneddata must contain only the full previous request (for compatibility issues).
  if oldsigneddata_is_fullrequest=False, only the signature must be specified for oldsigneddata
  """

  returned_comments = []

# we likely only want to keep the signature data around in many cases.   For 
# example, if the request is huge.   
#  if not signeddata_issignedcorrectly(oldsigneddata, publickey):
#    raise ValueError, "Old signed data is not correctly signed!"

  if not signeddata_issignedcorrectly(newsigneddata, publickey):
    returned_comments.append("Bad signature")
    return False, returned_comments
    
  # extract information about the current signature
  newjunk, newpubkey, newtime, newexpire, newsequence, newdestination = signeddata_split(newsigneddata)
  
  # get comments on everything but the timestamp and sequence number
  returned_comments = returned_comments + signeddata_getcomments(newsigneddata, publickey)
  
  #BUG FIX: only if the oldmetadata is not set to None, we want to split it and verify it
  if oldsigneddata != None :
  
    if (oldsigneddata_is_fullrequest):
      oldjunk, oldpubkey, oldtime, oldexpire, oldsequence, olddestination = signeddata_split(oldsigneddata)
    else:
      oldrawpublickey, oldrawtimestamp, oldrawexpiration, oldrawsequenceno, oldrawdestination, oldjunksignature = oldsigneddata.rsplit('!',5)
      oldpubkey, oldtime, oldexpire, oldsequence, olddestination = rsa_string_to_publickey(oldrawpublickey[1:]), signeddata_string_to_timestamp(oldrawtimestamp), signeddata_string_to_expiration(oldrawexpiration), signeddata_string_to_sequencenumber(oldrawsequenceno), signeddata_string_to_destination(oldrawdestination)
    
  

    # get comments on everything but the timestamp and sequence number
    returned_comments = returned_comments + signeddata_getcomments(newsigneddata, publickey)
  
    # check the sequence number data...
    if not signeddata_has_good_sequence_transition(oldsequence, newsequence):
      returned_comments.append('Invalid sequence transition')

    # check the timestamps...  
    if (newtime == None and oldtime != None) or oldtime == None or oldtime > newtime:
      # if the timestamps are reversed (None is the earliest possible)
      returned_comments.append('Timestamps out of order')
    elif oldtime != None and newtime != None and oldtime == newtime:
      # the timestamps are equal but not none...
      returned_comments.append('Timestamps match')
    else:   # So they either must both be None or oldtime < newtime
      assert((newtime == oldtime == None) or oldtime < newtime)
  

  # let's see what happened...
  if returned_comments == []:
    return True, []
  for comment in returned_comments:
    if comment in signeddata_fatal_comments:
      return False, returned_comments

    # if not a failure, should be a warning comment
    assert(comment in signeddata_warning_comments)

  # Warnings, so I won't return True
  return None, returned_comments
  

#end include signeddata.repy
#begin include sha.repy
#already included sha.repy
#end include sha.repy
#begin include rsa.repy
#already included rsa.repy
#end include rsa.repy
#begin include time.repy
#already included time.repy
#end include time.repy


#takes a message and public,private keys as parameters.
#returns a signature of the message. The signature uses the symbol '#' instead of 'space'
def cncSignData_get_message_signature(message, privatekey, publickey):
  base_signature = signeddata_create_signature(message, privatekey, publickey)
  signature = str(base_signature).replace(' ','#')
  return signature
  
  
#checks if a message is signed correctly
def cncSignData_check_signature(message, signature, publickey):
  signature = signature.replace('#',' ')
  try: 
    # extract the hash from the signature
    signedhash = rsa_verify(signature, publickey)
  except TypeError, e:
    if 'RSA' not in str(e):
      raise
    # Bad signature or public key
    return False

  # Does the hash match the signed data?
  if signedhash == sha_hash(message):
    return True
  else:
    return False
    
    
#checks is the timestamp is valid
#returns a pair of form (bool,string), where the first value is True or False indicating if the timestamp is valid,
#and the second is a string indicating that explains why the timestamp is invalid in the event it is.
def cncSignData_checktimestamp(timestamp, expiration_interval):
  #first check that the timestamp is in fact a float
  float_timestamp = None
  try:
    float_timestamp = float(timestamp)
  except Exception, e:
    #casting failed
    return (False,"cncSignData_checktimestamp: timestamp cannot be cast to a float")
    
  #check if timestamp is expired.
  if not(signeddata_iscurrent(float_timestamp+expiration_interval)):
    return (False,"cncSignData_checktimestamp: timestamp is expired, timestamp="+timestamp + ", expiration_interval="+str(expiration_interval))
  
  return (True,None)
  
#helper method that signes a message. The signed mesage is returned with the followign components appended: publickey timestamp signature
#the signature uses a hash that includes that publickey and timestamp.
def cncSignData_sign_message(message, publickey, privatekey):
  signed_message = message
  
  #add the public key of the current server and the timestamp
  local_public_key_string = rsa_publickey_to_string(publickey).replace(' ','#')
  signed_message = signed_message + " " + local_public_key_string + " " + str(time_gettime())
    
  #add the signature
  message_signature = cncSignData_get_message_signature(signed_message, privatekey, publickey)
  signed_message = signed_message + " " + message_signature
  return signed_message
  

#end include cncSignData.repy
#begin include nmclient.repy
""" 
Author: Justin Cappos

Module: Routines that interact with a node manager to perform actions on
        nodes.   A simple front end can be added to make this a functional
        experiment manager.

Start date: September 7th 2008

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

"""

# for signing the data we send to the node manager
#begin include signeddata.repy
#already included signeddata.repy
#end include signeddata.repy

# session wrapper (breaks the stream into messages)
# an abstracted "itemized data communication" in a separate API
#begin include session.repy
# This module wraps communications in a signaling protocol.   The purpose is to
# overlay a connection-based protocol with explicit message signaling.   
#
# The protocol is to send the size of the message followed by \n and then the
# message itself.   The size of a message must be able to be stored in 
# sessionmaxdigits.   A size of -1 indicates that this side of the connection
# should be considered closed.
#
# Note that the client will block while sending a message, and the receiver 
# will block while recieving a message.   
#
# While it should be possible to reuse the connectionbased socket for other 
# tasks so long as it does not overlap with the time periods when messages are 
# being sent, this is inadvisable.

class SessionEOF(Exception):
  pass

sessionmaxdigits = 20

# get the next message off of the socket...
def session_recvmessage(socketobj):

  messagesizestring = ''
  # first, read the number of characters...
  for junkcount in range(sessionmaxdigits):
    currentbyte = socketobj.recv(1)

    if currentbyte == '\n':
      break
    
    # not a valid digit
    if currentbyte not in '0123456789' and messagesizestring != '' and currentbyte != '-':
      raise ValueError, "Bad message size"
     
    messagesizestring = messagesizestring + currentbyte

  else:
    # too large
    raise ValueError, "Bad message size"

  messagesize = int(messagesizestring)
  
  # nothing to read...
  if messagesize == 0:
    return ''

  # end of messages
  if messagesize == -1:
    raise SessionEOF, "Connection Closed"

  if messagesize < 0:
    raise ValueError, "Bad message size"

  data = ''
  while len(data) < messagesize:
    chunk =  socketobj.recv(messagesize-len(data))
    if chunk == '': 
      raise SessionEOF, "Connection Closed"
    data = data + chunk

  return data

# a private helper function
def session_sendhelper(socketobj,data):
  sentlength = 0
  # if I'm still missing some, continue to send (I could have used sendall
  # instead but this isn't supported in repy currently)
  while sentlength < len(data):
    thissent = socketobj.send(data[sentlength:])
    sentlength = sentlength + thissent



# send the message 
def session_sendmessage(socketobj,data):
  header = str(len(data)) + '\n'
  session_sendhelper(socketobj,header)

  session_sendhelper(socketobj,data)




#end include session.repy


# makes connections time out
#begin include sockettimeout.repy
"""
<Description>
  Puts back in Python's non-blocking functionality.

  send():
    Raises SocketTimeout Error if the send call lasts
    longer than the set timeout.

  recv():
    Guarentees the receipt of a message.   Raises SocketTimeoutError if it does not
    receive any message before a given timeout.
    If actually receives the message, returns the message and continues.

<Usage>
  Text-replacable for Repy Sockets:
    timeout_openconn(desthost, destport, localip=None, localport=None, timeout = 5)
    timeout_waitforconn(localip, localport, function)

  Object:
    sockobj.settimeout(seconds)
    sockobj.send(data)
    sockobj.recv(bytes)
    sockobj.close()

<Date>
  Sun Mar  1 10:27:35 PST 2009

<Example>
  # hello world
  include sockettimer.repy

  def callback(ip, port, timeout_sockobj, commhandle, listenhandle):
    hw_message = timeout_sockobj.recv(1047)

    # cleanup
    stopcomm(commhandle)
    stopcomm(listenhandle)
    timeout_sockobj.close()

    print hw_message # => "hello world!"
  
  def server():
    sockobj = timeout_waitforconn(getmyip(), 12345, callback)

  def client():
    sockobj = timeout_openconn(getmyip(), 12345)
    sockobj.send("hello world!")

  def main():
    server()
    client()
    exitall()

  if callfunc == 'initialize':
    main() 
"""

class SocketTimeoutError(Exception):
  """The socket timed out before receiving a response"""

def timeout_openconn(desthost, destport, localip=None, localport=None, timeout = 5):
  """
  <Purpose> 
    Wrapper for Repy like socket interface

  <Args>
    Same as Repy openconn

  <Exception>
    Timeout exception if the dest address doesnt respond.

  <Returns>
    socket obj on success
  """

  tsock = TimeoutSocket()
  tsock.settimeout(timeout)
  if localip and localport:
    tsock.bind((localip, localport))
  tsock.connect((desthost, destport))
  return tsock

def timeout_waitforconn(localip, localport, function):
  """
  <Purpose> 
    Wrapper for Repy like socket interface

  <Args>
    Same as Repy waitforconn

  <Side Effects>
    Sets up event listener which calls function on messages.

  <Returns>
    Handle to listener.
  """

  tsock = TimeoutSocket()
  tsock.bind((localip, localport))
  tsock.setcallback(function)
  return tsock.listen()

class TimeoutSocket:
  """
  <Purpose>
    Provide an socket object like the Repy usual one.

  <Side Effects>
    Uses a getlock() to watch for a timeout
    Uses waitforconn and openconn to simulate socket
  """

  ################
  # Constructors
  ################

  def __init__(self):
    """ Constructor for socket """
#    self.lock = getlock() # general lock BUG: Do we need to lock everything?
    self.timeout_lock = getlock() # special lock for Timeout condition
    self.timeout = 5 # seconds to wait
    self.bytes_sent = None # used to check if send() timed out

    # user vars   
    self.local_address = None # ip, port
    self.remote_address = None # ip, port
    self.callback = None # the user's function to call

    # repy socket vars
    self.sockobj = None #  the Repy socket
    self.commhandle = None # the current comm
    self.listencommhandle = None # the listener comm


  ################
  # Mutator methods
  #################

  def settimeout(self, value):
    """ Setter for timeout"""
    self.timeout = value

  def setcallback(self, function):
    """ Setter for callback function"""
    self.callback = function

  ####################
  # Public Methods
  ####################

  def bind(self, local_address = None):
    """
    <Purpose>
      Set local address

    <Args>
      Tuple of (ip, port) local.
    """
    self.local_address = local_address

  def listen(self):
    """
    <Purpose>
      Listen for peer
    
    <Side Effects>
      Calls Repy waitforconn()
    """
    return self._waitforconn()

  def connect(self, remote_address):
    """
    <Purpose>
      Connect to peer.

    <Args>
      Tuple of (ip, port) remote.
   
    <Side Effects>
      Calls Repy openconn.
    """
    self.remote_address = remote_address
    self._openconn()

  def recv(self, maxLen): # timeout as optional arg ???
    """
    <Purpose>
      If it fails to finish within the timeout, I close the socket and raise a
      TimeoutError exception. I.e. if there's no message, we call it an error
      and raise it.
      
    <Arguments>
      maxLen - bytes to recv

    <Exception>
      Raises TimeoutError exception if the recv times out
      without receiving a message.

    <Side Effects>
      Closes the connection if times out.

    <Returns>
      The message.
    """
    return self._recv_or_close(maxLen)

  def send(self, data):
    """
    <Purpose>
      Just like normal Repy socket.  Sends messages.
      
    <Arguments>
      data - the string message

    <Exception>
      Same as Repy socket.
 
    <Returns>
      The bytes sent.
    """
    return self._send_or_close(data)

  def close(self):
    self.local_address = None # ip, port
    self.remote_address = None # ip, port
    self.callback = None # the user's function to call

    if self.sockobj:
      self.sockobj.close()
    self.sockobj = None #  the Repy socket
    if self.commhandle: stopcomm(self.commhandle)
    self.commhandle = None # the current comm
    if self.listencommhandle: stopcomm(self.listencommhandle)
    self.listencommhandle = None # the listener comm


  ########################
  # Private
  #########################

  def _openconn(self):
    """Handle current state variables and call Repy openconn."""

    destip, destport = self.remote_address
    if self.local_address:
      srcip, srcport = self.local_address
      self.sockobj = openconn(destip, destport, srcip, srcport, self.timeout)
    else:
      self.sockobj = openconn(destip, destport)

  def _waitforconn(self):
    """Setup way between Repy waitforconn event"""
    localip, localport = self.local_address
    self.listencommhandle = waitforconn(localip, localport, self._callback)
    return self.listencommhandle

  def _callback(self, ip, port, sockobj, ch, lh):
    """Pass on through to user callback"""
    self.sockobj = sockobj
    self.listencommhandle = lh # same as the 1st from wait for comm, right?
    self.commhandle = ch # should we care?
    
    if not self.remote_address:
      self.remote_address = (ip, port)
    else: 
      raise Exception("what! peer does not match?")

    self.callback(ip, port, self, ch, lh)

  def _send(self, data):
    """Send data"""
    return self.sockobj.send(data)

  def _recv(self, maxLen):
    """Recv data of length maxLen"""
    return self.sockobj.recv(maxLen)

  def _send_and_release(self, data):
    """Send data then release the timeout lock"""
    self.bytes_sent = self._send(data)
 
    self._quietly_release() # release the lock
 
  def _quietly_release(self):
    """Release the timeout lock and ignore if already released"""
    try:
      self.timeout_lock.release()
    except:
      pass
   
  def _send_or_close(self, data):
    """Raise the Timeout Error if no receipt.  Keep track by timeout_lock."""

    # acquire the lock, when it's release we'll carry on
    self.timeout_lock.acquire()

    # fork off a lock that'll release the lock at the timeout
    timerhandle = settimer(self.timeout, self._quietly_release, ())

    # fork off a send call so we can raise the exception in the main thread
    # the send call will also release our lock
    settimer(0, self._send_and_release, (data,))

    # block until either the timeout or _send finishes
    self.timeout_lock.acquire()
    self.timeout_lock.release()

    if self.bytes_sent: # send finished
      canceltimer(timerhandle)
      retdata = self.bytes_sent
      self.bytes_sent = None
      return retdata
    else: # it timed out
      self.close()
      raise SocketTimeoutError

  def _recv_or_close(self, amount):
    """Raise the Timeout Error if no receipt.  Keep track by timeout_lock."""
    timerhandle = settimer(self.timeout, self._clobbersocket, ())
    try:
      retdata = self._recv(amount)
    except Exception, e:
      # if it's not the timeout, reraise...
      if self.timeout_lock.acquire(False):
        raise
      raise SocketTimeoutError
    
    # I acquired the lock, I should stop the timer because I succeeded...
    if self.timeout_lock.acquire(False):
      # even if this isn't in time, the lock prevents a race condition 
      # this is merely an optimization to prevent the timer from ever firing...
      canceltimer(timerhandle)
      self.timeout_lock.release() # Alper's bug 3/10/09
      return retdata
    else:
      raise SocketTimeoutError

  def _clobbersocket(self):
    """If I can acquire the lock without blocking, then close the socket to abort"""
    if self.timeout_lock.acquire(False):
      self.close()


############################
# Deprecated functions
##############################

# private function...
def sockettimeout_clobbersocket(sockobj,mylock):
  # if I can acquire the lock without blocking, then close the socket to abort
  if mylock.acquire(False):
    sockobj.close()

# if it fails to finish within the timeout, I close the socket and raise a
# SocketTimeout exception...
def sockettimeout_recv_or_close(sockobj, amount, timeout):
  # A lock I'll use for this attempt
  mylock = getlock()
  timerhandle = settimer(timeout,clobbersocket, (sockobj, mylock))
  try:
    retdata = sockobj.recv(amount)
  except Exception, e:
    # if it's not the timeout, reraise...
    if mylock.acquire(False):
      raise
    raise SocketTimeout
    
  # I acquired the lock, I should stop the timer because I succeeded...
  if mylock.acquire(False):
    # even if this isn't in time, the lock prevents a race condition 
    # this is merely an optimization to prevent the timer from ever firing...
    canceltimer(timerhandle)
    return retdata
  else:
    raise SocketTimeout


#end include sockettimeout.repy

# The idea is that this module returns "node manager handles".   A handle
# may be used to communicate with a node manager and issue commands.   If the
# caller wants to have a set of node managers with the same state, this can
# be done by something like:
#
#
# myid =    # some unique, non-repeating value
# nmhandles = []
# for nm in nodemanagers:
#   nmhandles.append(nmclient_createhandle(nm, sequenceid = myid))
#
# 
# def do_action(action):
#   for nmhandle in nmhandles:
#     nmclient_doaction(nmhandle, ... )
#
#
# The above code snippet will ensure that none of the nmhandles perform the
# actions called in do_action() out of order.   A node that "misses" an action
# (perhaps due to a network or node failure) will not perform later actions 
# unless the sequenceid is reset.
#
# Note that the above calls to nmclient_createhandle and nmclient_doaction 
# should really be wrapped in try except blocks for NMClientExceptions



# Thrown when a failure occurs when trying to communicate with a node
class NMClientException(Exception):
  pass

# This holds all of the client handles.   A client handle is merely a 
# string that is the key to this dict.   All of the information is stored in
# the dictionary value (a dict with keys for IP, port, sessionID, timestamp,
# identity, expirationtime, public key, private key, and vesselID).   
nmclient_handledict = {}

# BUG: How do I do this and have it be portable across repy <-> python?
# needed when assigning new handles to prevent race conditions...
nmclient_handledictlock = getlock()



# Note: I open a new connection for every request.   Is this really what I want
# to do?   It seemed easiest but likely has performance implications

# Sends data to a node (opens the connection, writes the 
# communication header, sends all the data, receives the result, and returns
# the result)...
def nmclient_rawcommunicate(nmhandle, *args):

  try:
    thisconnobject = timeout_openconn(nmclient_handledict[nmhandle]['IP'], nmclient_handledict[nmhandle]['port'],timeout=nmclient_handledict[nmhandle]['timeout']) 
  except Exception, e:
    raise NMClientException, str(e)

  # always close the connobject
  try:

    # send the args separated by '|' chars (as is expected by the node manager)
    session_sendmessage(thisconnobject, '|'.join(args))
    return session_recvmessage(thisconnobject)
  except Exception, e:
    raise NMClientException, str(e)
  finally:
    thisconnobject.close()




# Sends data to a node (opens the connection, writes the 
# communication header, sends all the data, receives the result, and returns
# the result)...
def nmclient_signedcommunicate(nmhandle, *args):

  # need to check lots of the nmhandle settings...

  if nmclient_handledict[nmhandle]['timestamp'] == True:
    # set the time based upon the current time...
    timestamp = time_gettime()
  elif not nmclient_handledict[nmhandle]['timestamp']:
    # we're false, so set to None
    timestamp = None
  else:
    # For some reason, the caller wanted a specific time...
    timestamp = nmclient_handledict[nmhandle]['timestamp']

  if nmclient_handledict[nmhandle]['publickey']:
    publickey = nmclient_handledict[nmhandle]['publickey']
  else:
    raise NMClientException, "Must have public key for signed communication"

  if nmclient_handledict[nmhandle]['privatekey']:
    privatekey = nmclient_handledict[nmhandle]['privatekey']
  else:
    raise NMClientException, "Must have private key for signed communication"

  # use this blindly (None or a value are both okay)
  sequenceid = nmclient_handledict[nmhandle]['sequenceid']

  if nmclient_handledict[nmhandle]['expiration']:
    if timestamp == None:
      # highly dubious.   However, it's technically valid, so let's allow it.
      expirationtime = nmclient_handledict[nmhandle]['expiration']
    else:
      expirationtime = timestamp + nmclient_handledict[nmhandle]['expiration']

  else:
    # they don't want this to expire
    expirationtime = nmclient_handledict[nmhandle]['expiration']


  # use this blindly (None or a value are both okay)
  identity = nmclient_handledict[nmhandle]['identity']


  # build the data to send.   Ideally we'd do: datatosend = '|'.join(args)
  # we can't do this because some args may be non-strings...
  datatosend = args[0]
  for arg in args[1:]:
    datatosend = datatosend + '|' + str(arg)
    

  try:
    thisconnobject = timeout_openconn(nmclient_handledict[nmhandle]['IP'], nmclient_handledict[nmhandle]['port'], timeout=nmclient_handledict[nmhandle]['timeout'])
  except Exception, e:
    raise NMClientException, str(e)

  # always close the connobject afterwards...
  try:
    try:
      signeddata = signeddata_signdata(datatosend, privatekey, publickey, timestamp, expirationtime, sequenceid, identity)
    except ValueError, e:
      raise NMClientException, str(e)

    try:
      session_sendmessage(thisconnobject, signeddata)
    except Exception, e:
      # label the exception and change the type...
      raise NMClientException, "signedcommunicate failed on session_sendmessage with error '"+str(e)+"'"

    try:
      message = session_recvmessage(thisconnobject)
    except Exception, e:
      # label the exception and change the type...
      raise NMClientException, "signedcommunicate failed on session_recvmessage with error '"+str(e)+"'"

    return message
  finally:
    thisconnobject.close()



def nmclient_safelygethandle():
  # I lock to prevent a race when adding handles to the dictionary.   I don't
  # need a lock when removing because a race is benign (it prevents reuse)
  nmclient_handledictlock.acquire()
  try:
    potentialhandle = randomfloat()
    while potentialhandle in nmclient_handledict:
      potentialhandle = randomfloat()
    return potentialhandle
  finally:
    nmclient_handledictlock.release()





# Create a new handle, the IP, port must be provided but others are optional.
# The default is to have no sequenceID, timestamps on, expiration time of 1 
# hour, and the program should set and use the identity of the node.   The 
# public key, private key, and vesselids are left uninitialized unless 
# specified elsewhere.   Regardless, the keys and vesselid are not used to 
# create the handle and so are merely transfered to the created handle.
def nmclient_createhandle(nmIP, nmport, sequenceid = None, timestamp=True, identity = True, expirationtime = 60*60, publickey = None, privatekey = None, vesselid = None, timeout=10):

  thisentry = {}

  thisentry['IP'] = nmIP
  thisentry['port'] = nmport
  thisentry['sequenceid'] = sequenceid
  thisentry['timestamp'] = timestamp
  thisentry['expiration'] = expirationtime
  thisentry['publickey'] = publickey
  thisentry['privatekey'] = privatekey
  thisentry['vesselid'] = vesselid
  thisentry['timeout'] = timeout

    
  newhandle = nmclient_safelygethandle()

  nmclient_handledict[newhandle] = thisentry

  # Use GetVessels as a "hello" test (and for identity reasons as shown below)
  try:
    response = nmclient_rawsay(newhandle, 'GetVessels')

  except (ValueError, NMClientException, KeyError), e:
    del nmclient_handledict[newhandle]
    raise NMClientException, e


  # set up the identity
  if identity == True:
    for line in response.split('\n'):
      if line.startswith('Nodekey: '):
        # get everything after the Nodekey as the identity
        nmclient_handledict[newhandle]['identity'] = line[len('Nodekey: '):]
        break
        
    else:
      raise NMClientException, "Do not understand node manager identity in identification"

  else:
    nmclient_handledict[newhandle]['identity'] = identity

  # it worked!
  return newhandle



def nmclient_duplicatehandle(nmhandle):
  newhandle = nmclient_safelygethandle()
  nmclient_handledict[newhandle] = nmclient_handledict[nmhandle].copy()
  return newhandle

# public.   Use this to clean up a handle
def nmclient_destroyhandle(nmhandle):
  try:
    del nmclient_handledict[nmhandle]
  except KeyError:
    return False
  return True
  

# public.   Use these to get / set attributes about the handles...
def nmclient_get_handle_info(nmhandle):
  if nmhandle not in nmclient_handledict:
    raise NMClientException, "Unknown nmhandle: '"+str(nmhandle)+"'"
  return nmclient_handledict[nmhandle].copy()


def nmclient_set_handle_info(nmhandle, dict):
  if nmhandle not in nmclient_handledict:
    raise NMClientException, "Unknown nmhandle: '"+str(nmhandle)+"'"
  nmclient_handledict[nmhandle] = dict


  

# Public:  Use this for non-signed operations...
def nmclient_rawsay(nmhandle, *args):
  fullresponse = nmclient_rawcommunicate(nmhandle, *args)

  try:
    (response, status) = fullresponse.rsplit('\n',1)
  except KeyError:
    raise NMClientException, "Communication error '"+fullresponse+"'"

  if status == 'Success':
    return response
  elif status == 'Error':
    raise NMClientException, "Node Manager error '"+response+"'"
  elif status == 'Warning':
    raise NMClientException, "Node Manager warning '"+response+"'"
  else:
    raise NMClientException, "Unknown status '"+fullresponse+"'"
  



# Public:  Use this for signed operations...
def nmclient_signedsay(nmhandle, *args):

  fullresponse = nmclient_signedcommunicate(nmhandle, *args)

  try:
    (response, status) = fullresponse.rsplit('\n',1)
  except KeyError:
    raise NMClientException, "Communication error '"+fullresponse+"'"

  if status == 'Success':
    return response
  elif status == 'Error':
    raise NMClientException, "Node Manager error '"+response+"'"
  elif status == 'Warning':
    raise NMClientException, "Node Manager warning '"+response+"'"
  else:
    raise NMClientException, "Unknown status '"+fullresponse+"'"
  


# public, use this to do raw communication with a vessel
def nmclient_rawsaytovessel(nmhandle, call, *args):
  vesselid = nmclient_handledict[nmhandle]['vesselid']
  if not vesselid:
    raise NMClientException, "Must set vesselid to communicate with a vessel"

  return nmclient_rawsay(nmhandle,call, vesselid,*args)
  


# public, use this to do a signed communication with a vessel
def nmclient_signedsaytovessel(nmhandle, call, *args):
  vesselid = nmclient_handledict[nmhandle]['vesselid']
  if not vesselid:
    raise NMClientException, "Must set vesselid to communicate with a vessel"

  return nmclient_signedsay(nmhandle,call, vesselid,*args)


# public, lists the vessels that the provided key owns or can use
def nmclient_listaccessiblevessels(nmhandle, publickey):

  vesselinfo = nmclient_getvesseldict(nmhandle)

  # these will be filled with relevant vessel names...
  ownervessels = []
  uservessels = []

  for vesselname in vesselinfo['vessels']:
    if publickey == vesselinfo['vessels'][vesselname]['ownerkey']:
      ownervessels.append(vesselname)

    if 'userkeys' in vesselinfo['vessels'][vesselname] and publickey in vesselinfo['vessels'][vesselname]['userkeys']:
      uservessels.append(vesselname)


  return (ownervessels, uservessels)



#public, parse a node manager's vessel information and return it to the user...
def nmclient_getvesseldict(nmhandle):

  response = nmclient_rawsay(nmhandle, 'GetVessels')

  retdict = {}
  retdict['vessels'] = {}

  # here we loop through the response and set the dicts as appropriate
  lastvesselname = None
  for line in response.split('\n'):
    if not line:
      # empty line.   Let's allow it...
      pass
    elif line.startswith('Version: '):
      retdict['version'] = line[len('Version: '):]
    elif line.startswith('Nodename: '):
      retdict['nodename'] = line[len('Nodename: '):]
    elif line.startswith('Nodekey: '):
      retdict['nodekey'] = rsa_string_to_publickey(line[len('Nodekey: '):])
 
    # start of a vessel
    elif line.startswith('Name: '):
      # if there is a previous vessel write it to the dict...
      if lastvesselname:
        retdict['vessels'][lastvesselname] = thisvessel

      thisvessel = {}
      # NOTE:I'm changing this so that userkeys will always exist even if there
      # are no user keys (in this case it has an empty list).   I think this is
      # the right functionality.
      thisvessel['userkeys'] = []
      lastvesselname = line[len('Name: '):]

    elif line.startswith('OwnerKey: '):
      thiskeystring = line[len('OwnerKey: '):]
      thiskey = rsa_string_to_publickey(thiskeystring)
      thisvessel['ownerkey'] = thiskey

    elif line.startswith('OwnerInfo: '):
      thisownerstring = line[len('OwnerInfo: '):]
      thisvessel['ownerinfo'] = thisownerstring

    elif line.startswith('Status: '):
      thisstatus = line[len('Status: '):]
      thisvessel['status'] = thisstatus

    elif line.startswith('Advertise: '):
      thisadvertise = line[len('Advertise: '):]
      if thisadvertise == 'True':
        thisvessel['advertise'] = True
      elif thisadvertise == 'False':
        thisvessel['advertise'] = False
      else:
        raise NMClientException, "Unknown advertise type '"+thisadvertise+"'"

    elif line.startswith('UserKey: '):
      thiskeystring = line[len('UserKey: '):]
      thiskey = rsa_string_to_publickey(thiskeystring)

      thisvessel['userkeys'].append(thiskey)

    else:
      raise NMClientException, "Unknown line in GetVessels response '"+line+"'"


  if lastvesselname:
    retdict['vessels'][lastvesselname] = thisvessel
  return retdict

#end include nmclient.repy

##Constants

#registering with this key will register the local machine on the repy query server
REPY_MEMBERSHIP_KEY = "repy_membership"

NUM_RETRIES = 4 #number of times to retry if the server cannot be contacted

#number of addresses to forward update packets to
NUM_FORWARDING_ADDRESSES=4

#indicates the time interval after a cached address expires
CACHED_ADDRESS_EXPIRATION_INTV = 1800.0

#gives the amount of time after creation at which an update packet is no longer accepted by repy nodes
UPDATE_PACKET_EXPIRATION_INTV = 600.0

#indicates the interval to wait inbetween checking each entry within a single iteration
EXPIRATION_CHECK_INTV_ENTRY = .05
EXPIRATION_CHECK_INTV_ITERATION = 20

#time until a renewal key expires
RENEWAL_KEY_EXP = 3600

#time until registration for an address expires
REGISTRATION_EXP = 120

#time between registration attempts
REGISTRATION_INTV = REGISTRATION_EXP-10
 
#in the case of a failure in registration, this is the interval we wait for before retrying
REGISTRATION_RETRY_INTV=3

#in the event the server is not responding to a UDP Packet, retry sending it on this interval
UDP_RETRY_INTERVAL = 3

#interval between polling to check if a reply was received to a UDP request
UDP_POLL_INTERVAL = .1

#how frequently to send a request to the server for the full list of nodes for a particular user key
DATA_UPDATE_INTERVAL = 15

#file containing information on update and query servers and their public keys
UPDATE_SERVER_FILE="update_query_server_list.txt"

#file containing information on registration servers and their public keys
REGISTRATION_SERVER_FILE = "registration_server_list.txt"

#interval after which a packet is considered expired, not used for update packets
PACKET_EXPIRATION_INTV = 20.0

##state variables

cncclient_context = {}

#type dict with keys consistiong of user keys and entries of type set.
#for example, user_node_table["user1"] gives a set of node ip addresses (only ip address, no port component) under the control of user1.
user_node_table = dict()

#the user_node_table, has a special entry at index QUERY_RESULT_SET_KEY. The set at this entry stores addresses 
#from VerifyAddress responses. This index is not modified by getaddresslist queries or AddressList updates
QUERY_RESULT_SET_KEY = "results_from_verify_address_requests"

#each key is an ip string. each entry is a (timestamp,port) pair. The timestamp value indicates the time the index ip's address expires.
address_info_table=dict()

#this lock managed access to the user_node_table and address_info_table. While holding the lock, it is guaranteed neither structure will change.
user_node_table_lock = getlock()

#indexed by user key, each entry is a timestamp, which is the timestamp of the last update packet that was processed for the respective userkey
last_update_processed = dict()

#renewal data to allow node to register through UDP
cncclient_context['renewal_key']=None
cncclient_context['renewal_key_expiration']= 0 #we initialize to 0 to avert race conditions in which we check expiration for a key whose expiration has not been set yet
renewal_lock = getlock()

#structure that allows for looking up the public key of any registration server
cncclient_context["reg_server_dict"] = dict() #each key is of the form <ip>:<port>. each entry is the public key

#structure that allows for looking up the public key of any update server
cncclient_context["update_query_server_dict"] = dict() #each key is of the form <ip>:<port>. each entry is the public key

#list of (ip,port) pairs indicating available registration servers.
cncclient_context["registration_server_list"]=None

#keeps track of the current registration server, (ip,port) pair
cncclient_context["current_registration_server"]=None

#keeps track of the port to be used for cnc communication
#port on which client connects and sends messages to the server, port on which client listents for cnc communication
cncclient_context["client_con_port"] = None

##variables used to store data received from the server. The exact unmodified reply is stored as the entry

cncclient_context['renewal_request_reply'] = None #reply for RenewAddressRequest requests
cncclient_getaddresslist_replies = {} #replies for GetAddressesForUserRequest requests


#structure that indicates the update servers with each key range
#each key is a pair of integers (lower user key, upper user key). Each entry is a list of (ip, port) pairs giving the address of the servers in the respective update unit. 
cncclient_context['update_key_range_table'] = None

#structure that keeps track of which query servers correspond to a given userkey
#each key is a userkey of type string. Each entry is a list of (ip, port) pairs giving the address of the servers in the query unit for the particular userkey. 
cncclient_context['query_server_table'] = None

#used to keep track of replies to GetUserKeyRangeTables requests
cncclient_context["keyrange_tables_reply"]=None


##external state data, this data reffers to the state of the node manager
#for now, filler data is used
#during integration with the node manager, this data will need to come from the node manager
user_key_test_list = ["user1_fssasfe","user2_avceeafe","user3_adfoneoi"]

##Fields used for caching userkeys from the nodemanager
#if the DEBUG_USERKEY_MODE flag is set to True, test data will be returned instead of the actual user keys
#the userkey list is cached and refreshed no more frequently than USER_KEY_LIST_REFRESH_INTV
DEBUG_USERKEY_MODE = False
cncclient_context["userkey_list_timestamp"] = 0.0
cncclient_context["current_userkey_list"]= []
USER_KEY_LIST_REFRESH_INTV=30.0


#throw when trying to send a packet or open a connection to an address not in the cache
class CncCacheMissException(Exception):
  pass

##helper functions

#function that is used to log messages, currently, input to this function is also printed
LOG_FILE_BASE_NAME="cncclientlog"
cncclient_context["logging_lock"]=getlock()
cncclient_context["log_file_handle"]=None
cncclient_context["logfile_created"]=0.0
cncclient_context["logfile_number"]=1
#every 10 minutes (600 secs), a new log file is created with the next number as a suffix, and the previous log file is closed
def write_to_log(message):
  print "log: "+message
  
  cncclient_context["logging_lock"].acquire()
  timestamp = str(time_gettime())
  data_to_write = timestamp+": " + message + "\n"
  
  #if there is no open file handle, create one
  if cncclient_context["log_file_handle"]==None:
    logfilename = LOG_FILE_BASE_NAME + "." + str(cncclient_context["logfile_number"])
    cncclient_context["log_file_handle"] = open(logfilename, 'w')
    cncclient_context["logfile_created"] = time_gettime()
    
  # if the current handle is 10 minutes or more old, close it
  current_time = time_gettime()
  if current_time > (cncclient_context["logfile_created"] + 600.0) : 
    #close the old file
    cncclient_context["logfile_number"]= cncclient_context["logfile_number"]+1
    cncclient_context["log_file_handle"].close()
    cncclient_context["log_file_handle"]=None
    
    #open a new file
    logfilename = LOG_FILE_BASE_NAME + "." + str(cncclient_context["logfile_number"])
    cncclient_context["log_file_handle"] = open(logfilename, 'w')
    cncclient_context["logfile_created"] = time_gettime()
    
  
  #write to the log file
  cncclient_context["log_file_handle"].write(data_to_write)
  
  cncclient_context["logging_lock"].release()


#returns the list of local user keys, each user key is a string
#the keys returned are not teh actual node user keys, but rather hashes of the node userkeys.
userkey_list_lock = getlock() #to ensure caching is handled properly, controls writing the cached list
def get_userkey_list():
  #TODO, do something better here, not just use test data set as constant
  if DEBUG_USERKEY_MODE:
    return user_key_test_list
    
  #if the current userkey list is recent, return it
  if(time_gettime() < cncclient_context["userkey_list_timestamp"]+USER_KEY_LIST_REFRESH_INTV):
    return cncclient_context["current_userkey_list"]
  
  userkey_list_lock.acquire()
  
  #another thread may have already gotten the new user key list while we waited for the lock
  if(time_gettime() < cncclient_context["userkey_list_timestamp"]+USER_KEY_LIST_REFRESH_INTV):
    userkey_list_lock.release()
    return cncclient_context["current_userkey_list"]
    
  #get the list of userkeys on the vessel
  try:
    nmhandle = nmclient_createhandle(getmyip(), 1224)
    vessel_dict = nmclient_getvesseldict(nmhandle)
  except Exception, e:
    #an internal error has occured. Log it.
    write_to_log("Error Has Trying to get Node key list: " + str(e))
    userkey_list_lock.release()
    return []
    
  #get the userkeys from the vessel dict
  nodekeys_result = []
  if("vessels" in vessel_dict.keys()):
    for vessel_id in vessel_dict["vessels"].keys():
      if "userkeys" in vessel_dict["vessels"][vessel_id].keys():
        userkeys = vessel_dict["vessels"][vessel_id]["userkeys"]
        for userkey in userkeys:
          cnc_userkey = keyrangelib_publickey_to_cncuserkey(userkey)
          nodekeys_result.append(cnc_userkey)
          
  if("vessels" in vessel_dict.keys()):
    for vessel_id in vessel_dict["vessels"].keys():
      if "ownerkey" in vessel_dict["vessels"][vessel_id].keys():
        ownerkey = vessel_dict["vessels"][vessel_id]["ownerkey"]
        cnc_ownerkey = keyrangelib_publickey_to_cncuserkey(ownerkey)
        nodekeys_result.append(cnc_ownerkey)
  
  #cache the result
  cncclient_context["userkey_list_timestamp"]=time_gettime()
  cncclient_context["current_userkey_list"] = nodekeys_result
  userkey_list_lock.release()
  
  
  return nodekeys_result

#returns a list of users on the node of the format:
#user1,user2,user3,...
def get_user_list_string():
  user_key_list = get_userkey_list()
  
  if len(user_key_list)<1:
   return ""
 
  user_string = ""
  for user_key in user_key_list:
    user_string = user_string+user_key + ","
    
  #don't include the trailing comma
  return user_string[0:len(user_string)-1]


#parses the keys of cncclient_context["reg_server_dict"] to construct a list of registration servers
def cncclient_getRegistrationServerList():
  result_list = []
  
  reg_dict_keys = cncclient_context["reg_server_dict"].keys()
  for entry in reg_dict_keys:
    #split the entry to ip and port
    entry_ip, entry_port_str = entry.split(':')
    entry_port = int(entry_port_str)
    entry_to_add = (entry_ip, entry_port)
    result_list.append(entry_to_add)
    
  return result_list
  

#sets the current registration server address to be used to a randomly chosen registration server.
def cncclient_reset_registration_server_address():
  #pick an index randomly
  r = random_randint(0,len(cncclient_context["registration_server_list"])-1)
  cncclient_context["current_registration_server"] = cncclient_context["registration_server_list"][r]
  return


#udpdates the update_key_range_table and query_server_table structures
#this function blocks until complete.
def cncclient_update_key_range_and_query_tables():
  cncclient_context["keyrange_tables_reply"]=None
  
  for attempt in range(0,NUM_RETRIES):
    
    sendmess(cncclient_context["current_registration_server"][0], cncclient_context["current_registration_server"][1], "GetUserKeyRangeTables", localip=getmyip(), localport=cncclient_context["client_con_port"])
      
    #wait and poll to check if a reply has been received
    time_to_wait = UDP_RETRY_INTERVAL
    while time_to_wait>0 :
      time_to_wait = time_to_wait - UDP_POLL_INTERVAL
        
      #if we have a reply break
      if cncclient_context["keyrange_tables_reply"]!=None :
        break
        
      #otherwise, sleep and keep trying
        
      sleep(UDP_POLL_INTERVAL)
        
    #if we have a reply break
    if cncclient_context["keyrange_tables_reply"]!=None :
      break
    
    #we do not have a reply, so write to the log
    write_to_log("GetUserKeyRangeTables: Unable to get reply from server, timeout set to " + str(UDP_RETRY_INTERVAL) + " seconds.")
    
  #if after all the retries,we did not get response, try using a different registration server
  if cncclient_context["keyrange_tables_reply"]==None:
    write_to_log("Registration server" + str(cncclient_context["current_registration_server"]) + " is not responding to GetUserKeyRangeTables requests, changing registration server")
    cncclient_reset_registration_server_address()
    
    #retry with the new registration server address
    cncclient_update_key_range_and_query_tables()
    return
    
  #we did get a reply
  keyrangetablemessage, remoteip, remoteport = cncclient_context["keyrange_tables_reply"]  
  parsed_data = keyrangetablemessage.split()
  server_tag = remoteip+":" + str(remoteport)
 
  
  #check public key in message
  message_public_key_str = parsed_data[3].replace('#',' ')
  message_public_key = rsa_string_to_publickey(message_public_key_str)
  
  if(not(message_public_key in cncclient_context["reg_server_dict"].values())):
    #public keys dont match
    write_to_log("message public key -" + message_public_key_str+ "- was not found in reg_server_dict")
    
    #retry recursively
    cncclient_update_key_range_and_query_tables()
    return
  
  #check the timestamp
  valid, reason = cncSignData_checktimestamp(parsed_data[4], PACKET_EXPIRATION_INTV)
  if not(valid):
    write_to_log("timestamp check failed: " + reason + " message="+ keyrangetablemessage)
    
    #retry recursively
    cncclient_update_key_range_and_query_tables()
    return
    
  message_part, signature_part = keyrangetablemessage.rsplit(' ',1)
  signature_correct = cncSignData_check_signature(message_part, signature_part, message_public_key)
  if not(signature_correct):
    write_to_log("signature check failed on GetUserKeyRangeTablesReply packet. Resending request.")
    
    #retry recursively
    cncclient_update_key_range_and_query_tables()
    return
  
  #the packet is valid. parse it and store content.
  cncclient_context['update_key_range_table'] = keyrangelib_parse_update_key_ranges_string(parsed_data[1])
  cncclient_context['query_server_table'] = keyrangelib_parse_query_table_string(parsed_data[2])
  return

#slowly iterates through the entries in the address_info_table dict and removes any that are expired
def cncclient_cleanup_address_info_table():
  while True:
    for index_address in address_info_table.keys():
      
      #if the address is expired, remove the entry from this table and the user_node_table
      user_node_table_lock.acquire()
      if address_info_table[index_address][0] < time_gettime() :
        write_to_log("deleting " + str(index_address) + " from cache, address is expired")
        address_info_table.pop(index_address)
        
        #check entries under each user key index in the node_address_table
        for userkey_index in user_node_table.keys():
          if index_address in user_node_table[userkey_index]:
            user_node_table[userkey_index].remove(index_address)
      
      #we cleared the expired entries, so release the lock
      user_node_table_lock.release()
      
      #sleep a short time to allow other threads that need the lock to work
      sleep(EXPIRATION_CHECK_INTV_ENTRY)
      
    #sleep a long time before starting the next iteration
    sleep(EXPIRATION_CHECK_INTV_ITERATION)
    
##Cache Verification
#checks if given address is in the cache. returns True or False
def verify_address_in_cache(address_ip):

  #we need the lock to make sure the data in the cache stays consistent while we go through these checks
  user_node_table_lock.acquire()

  #if there is no entry for the address in the address info table, it is not in the cache so return
  if not(address_ip in address_info_table.keys()):
    user_node_table_lock.release()
    write_to_log("cache miss: " + str(address_ip) + " not in address info table")
    return False
  
  #if the address ip is expired, return false right away
  timestamp,port = address_info_table[address_ip]
  if (timestamp < time_gettime()):
    user_node_table_lock.release()
    write_to_log("cache miss: " + str(address_ip) + " in address info table, but is expired")
    return False

  for indexing_userkey in user_node_table.keys():
    if address_ip in user_node_table[indexing_userkey]:
      user_node_table_lock.release()
      write_to_log("cache hit: " + str(address_ip) + " found in user node table")
      return True;
  
  #we did not find the address, so return false
  user_node_table_lock.release()
  write_to_log("cache miss: " + str(address_ip) + " found in info table, but not in user node table.")
  return False


##restricting the sending of traffic

#if specified address is not in the cache, throws a CncCacheMissException, and sends a verify address request to the 
# query server that has key REPY_MEMBERSHIP_KEY
def cnc_restrict_traffic(ip_address):

  #if the ip_address is in the cache, return
  if(verify_address_in_cache(ip_address)):
    return
    
  #address is not in the cache
  #get the list of query server addresses for the REPY_MEMBERSHIP_KEY
  #get the address of a server that handles this userkey
  server_address_list = keyrangelib_get_addresses_for_userkey(REPY_MEMBERSHIP_KEY, cncclient_context['update_key_range_table'], cncclient_context['query_server_table'])
      
  #pick one of the addresses
  r = random_randint(0,len(server_address_list)-1)
  target_server_address = server_address_list[r]
      
  #send a request to the server
  request_message = "VerifyAddressRequest "+ REPY_MEMBERSHIP_KEY + " " + ip_address
  sendmess(target_server_address[0],target_server_address[1], request_message, localip=getmyip(), localport=cncclient_context["client_con_port"])
  
  raise CncCacheMissException, str("address: " + ip_address + " not found in cache.")

def cnc_sendmess(desthost, destport, message, localip=None, localport=0):
  cnc_restrict_traffic(desthost)
  sendmess(desthost, destport, message, localip, localport)
  return

def cnc_openconn(desthost, destport, localip=None, localport=0, timeout = 5):
  cnc_restrict_traffic(desthost)
  cnc_openconn(desthost, destport, localip, localport, timeout)
  return
  
##registration functions

#maintains registration with the server for a given user key
def cncclient_maintain_registration(renewal_key_invalid=None):
  #get the string representation of the base user list
  user_list_string = get_user_list_string()
  
  #add the REPY_MEMBERSHIP_KEY to the user list string
  if user_list_string == "":
    user_list_string = REPY_MEMBERSHIP_KEY
  else:
    user_list_string = user_list_string+ "," + REPY_MEMBERSHIP_KEY
  
  #check if the current renew key is expired, if so, set it to None so we save time and connect directly through TCP
  if (cncclient_context['renewal_key'] != None and cncclient_context['renewal_key_expiration'] < time_gettime()) :
    
    #we need to get the lock to the renewal data
    renewal_lock.acquire()
    
    #we need to verify again if the key is expired since it may have been changed by a thread since the lock was acquired
    if (cncclient_context['renewal_key'] != None and cncclient_context['renewal_key_expiration'] < time_gettime()) :
      cncclient_context['renewal_key'] = None
    renewal_lock.release()
    
  #check if the current renew key has been marked as invalid by the caller, if so, set the renew key to none
  if (cncclient_context['renewal_key'] != None and renewal_key_invalid != None):
  
    #we need to get the lock to the renewal data
    renewal_lock.acquire()
      
    #we need to verify again if the key is expired since it may have been changed by a thread since the lock was acquired
    if (cncclient_context['renewal_key'] != None and renewal_key_invalid != None):
      cncclient_context['renewal_key'] = None
    renewal_lock.release()
     
  #check if there is no renewal key available, if so, connect through TCP
  if cncclient_context['renewal_key']==None:
  
    #connect through TCP
    registered = False
    reply = None
    while not(registered):
      try:
        server_con_handle = openconn(cncclient_context["current_registration_server"][0], cncclient_context["current_registration_server"][1],localip=getmyip(), localport=cncclient_context["client_con_port"])
        #send the registration request
        server_con_handle.send('RegisterAddressRequest ' + user_list_string )
	reply = server_con_handle.recv(1024)
        server_con_handle.close()
        registered=True
      except Exception, e:
        write_to_log("Unable to open tcp connection to " + cncclient_context["current_registration_server"][0] + ":" + str(cncclient_context["current_registration_server"][1]))
        write_to_log("Exception thrown: " + str(e))
        write_to_log("Reseting default registration server and retrying.")
      
        #maybe use a different server instead
        cncclient_reset_registration_server_address()
            
        #try registering again in a short time, we do not exit this method untill the initial tcp registration is done
        sleep(REGISTRATION_RETRY_INTV)
      
      
    parsed_reply = reply.split()
      
    #check for failure to register
    if (parsed_reply[0]!="RegisterAddressRequestComplete") :
      write_to_log("TCP Registration failed, reply from server = " + reply)
        
      #use a different server instead
      cncclient_reset_registration_server_address()
      
      #try registering again in a short time
      settimer(REGISTRATION_RETRY_INTV,cncclient_maintain_registration,[])
      return
        
    #otherwise, registration was successful
    else:
      write_to_log("TCP Registration successful, reply from server = " + reply)
        
      #get the lock to the renew data
      renewal_lock.acquire()
      
      #store the renew key
      cncclient_context['renewal_key'] = parsed_reply[1]
        
      #compute the renew key expiration
      cncclient_context['renewal_key_expiration'] = time_gettime() + RENEWAL_KEY_EXP
      renewal_lock.release()
      
      #set an event for the next registration
      settimer(REGISTRATION_INTV,cncclient_maintain_registration,[])
      return
      
    #if there is a renew key available, connect through UDP
  else:
  
    #save the renew key we are using before sending the packet
    #in the case we fail, we can identify the invalid renewal key
    renewal_key_used = cncclient_context['renewal_key']
    
    #send a request for the full list of nodes for the user and listen for a reply
      
    #try sending untill we get a reply
    cncclient_context['renewal_request_reply'] = None
    for attempt in range(0,NUM_RETRIES):
        
      sendmess(cncclient_context["current_registration_server"][0], cncclient_context["current_registration_server"][1], "RenewAddressRequest " + user_list_string + " " + renewal_key_used, localip=getmyip(), localport=cncclient_context["client_con_port"])
          
      #wait and poll to check if a reply has been received
      time_to_wait = UDP_RETRY_INTERVAL
      while time_to_wait>0 :
        time_to_wait = time_to_wait - UDP_POLL_INTERVAL
            
        #if we have a reply break
        if cncclient_context['renewal_request_reply']!=None :
          break
            
        #otherwise, sleep and keep trying
            
        sleep(UDP_POLL_INTERVAL)
            
      #if we have a reply break
      if cncclient_context['renewal_request_reply']!=None :
        break
        
      #we do not have a reply, so write to the log
      write_to_log("RenewAddressRequest: Unable to get reply from server, timeout set to " + str(UDP_RETRY_INTERVAL) + " seconds")
        
    #if after all the retries,we did not get response, wrtie to log and exit the thread  
    if cncclient_context['renewal_request_reply']==None:
      write_to_log("registration server " + str(cncclient_context["current_registration_server"]) + " is not responding to renew requests")
      
      #use a different server instead
      cncclient_reset_registration_server_address()
          
      #try registering again in a short time
      settimer(REGISTRATION_RETRY_INTV,cncclient_maintain_registration,[])
      return

    
    reply = cncclient_context['renewal_request_reply']
    parsed_reply = reply.split()
      
    #check for failure to register
    #first check if the renewal key was expired or invallid
    if (parsed_reply[0]=="RenewFailedInvalidRenewalKey"):
      #mark the renew key used as invallid and make a recursive call
      write_to_log("UDP Renew failed due to invalid renewal key " + renewal_key_used + " , reply from server = " + reply)
      cncclient_maintain_registration(renewal_key_used)
        
    #ifthe renew failed for some other reason, log and retry later  
    elif (parsed_reply[0]!="RenewAddressRequestComplete") :
      write_to_log("UDP Renew failed, reply from server = " + reply)
              
      #try registering again in a short time
      settimer(REGISTRATION_RETRY_INTV ,cncclient_maintain_registration,[])
      return
      
    #otherwise, renew was successful
    else:
      write_to_log("UDP Renew Successful, reply from server = " + reply)
        
      #set an event for the next registration
      settimer(REGISTRATION_INTV,cncclient_maintain_registration,[])
      return


##functions involving updating the datatable

#adds the specified address to the cache under given userkey
#timestamp_float is the timestamp of the source packet.
#if no userkey is specified, we will add the address to user_node_table[QUERY_RESULT_SET_KEY]
def add_address_to_cache(address_ip, address_port, timestamp_float, userkey = QUERY_RESULT_SET_KEY):
  #we need to add this address to user_node_table if it is not already present
  user_node_table_lock.acquire()
      
  #if no set exists for the current userkey, create one
  if not(userkey in user_node_table.keys()):
    user_node_table[userkey] = set()
        
  #if address is not already in the table, add it
  if not(address_ip in user_node_table[userkey]):
    write_to_log(str(address_ip) + ":" + str(address_port) + " added to cache.")
    user_node_table[userkey].add(address_ip)
        
  #update the expiration value for the address, unless it is already set to a greater value
  new_exp_value = timestamp_float+CACHED_ADDRESS_EXPIRATION_INTV
      
  #if no expiration and port value is set in the table, set it now.
  if not(address_ip in address_info_table.keys()):
    address_info_table[address_ip] = (new_exp_value,address_port)
       
  #if value is already set in the table, only change it if current expiration value is greater  
  elif (new_exp_value > address_info_table[address_ip][0]):
    write_to_log("expiration time for address " + str(address_ip) + ":" + str(address_port) + " has been updated.")
    address_info_table[address_ip] = (new_exp_value,address_port)

  #we are done with this address, so release the lock
  user_node_table_lock.release()
  return

#sends queries to update servers to get the full list of addresses for each local userkey
def cncclient_address_list_query():
  while True:
    #used to avoid duplicates
    sent_keys = set()
    
    user_key_list = get_userkey_list()
    for user_key in user_key_list:
      #send the query for the userkey
      if not (user_key in sent_keys):
        cncclient_address_list_query_single_userkey(user_key)
        sent_keys.add(user_key)
      
    write_to_log("sent address list queries for " + str(len(sent_keys)) + " unique keys from " + str(len(user_key_list)) + " keys")
      
    #sleep 30 minutes before dong a full query again
    sleep(30*60)

#helper method that sends a querry for a full address list for a single user key
def cncclient_address_list_query_single_userkey(user_key):
  #get the address of a server that handles this userkey
  server_address_list = keyrangelib_get_addresses_for_userkey(user_key, cncclient_context['update_key_range_table'], cncclient_context['query_server_table'])
      
  #pick one of the addresses
  r = random_randint(0,len(server_address_list)-1)
  target_server_address = server_address_list[r]
      
  #send a request to the server
  sendmess(target_server_address[0],target_server_address[1], "GetAddressesForUserRequest "+ user_key, localip=getmyip(), localport=cncclient_context["client_con_port"])
  return


#processes replies from GetAddressesForUserRequest requests
#these replies include UserKeyNotFound packets and GetAddressesReply packets
def cncclient_process_address_list_message(remoteIP, remoteport, message):
  #parse the reply
  parsed_data = message.split()
  
  #if the number of tokens in the message is incorrect, return and ignore the message after logging
  if (len(parsed_data) < 5):
    write_to_log("address list message is in incorrect format, message = "+message)
    return
  
  message_part, signature_part = message.rsplit(' ',1)
  data, publickey_str, timestamp = message_part.rsplit(' ',2)
  
  #check public key in message
  message_public_key_str = publickey_str.replace('#',' ')
  message_public_key = rsa_string_to_publickey(message_public_key_str)
  
  if(not(message_public_key in cncclient_context["update_query_server_dict"].values())):
    #public keys dont match
    write_to_log("message public key -" + message_public_key_str+ "- was not found in update_query_server_dict")
    
    #message cannot be trused, so return
    return
  
  #check the timestamp
  valid, reason = cncSignData_checktimestamp(timestamp, PACKET_EXPIRATION_INTV)
  if not(valid):
    write_to_log("timestamp check failed: " + reason + " message="+ message)
    return
    
  signature_correct = cncSignData_check_signature(message_part, signature_part, message_public_key)
  if not(signature_correct):
    write_to_log("signature check failed on reply packet: " + message)
    return

  #packet is valid, so now process it
  
  #if the packet is of type UserKeyNotFound, refresh the keyrange and query tables and resend the getaddresses query
  if parsed_data[0]=="UserKeyNotFound":
    write_to_log("UserKeyNotFound packet received for userkey: " + parsed_data[1])
    write_to_log("Refreshing keyrange and query tables, and resending the address list query.")
    cncclient_update_key_range_and_query_tables()
    cncclient_address_list_query_single_userkey(parsed_data[1])
    return
    
  elif parsed_data[0]=="GetAddressesReply":
    #process the reply
    user_key = parsed_data[1]
    address_data = parsed_data[2]
    
    #get the lock to the user_node_table
    user_node_table_lock.acquire()

    write_to_log("processing full address list reply for userkey " + str(user_key))
    
    #overwrite the previous set in the user_node_table with an empty set
    user_node_table[user_key] = set()
    
    write_to_log("entries for userkey " + str(user_key)+ " have been cleared.")
    
    # if the address list is empty, release the lock and we are done.
    if address_data=="None":
      user_node_table_lock.release()
      return
    
    #each address_timestamp_fragment is a string of the format <address>:<timestamp>
    address_timestamp_fragments = address_data.split(',')
    for address_timestamp_fragment in address_timestamp_fragments:
      address_to_store = address_timestamp_fragment.split(':')[0]
      port_to_store = int(address_timestamp_fragment.split(':')[1])
      
      #store the address
      user_node_table[user_key].add(address_to_store)
      
      #set the expiration time of the address to the current time + CACHED_ADDRESS_EXPIRATION_INTV
      #set the port to waht was specified in the message
      address_info_table[address_to_store] = (time_gettime() + CACHED_ADDRESS_EXPIRATION_INTV, port_to_store)
      
      write_to_log(str(address_to_store) + " added to node cache.")
      
    #packet has been processed, so release the lock and return
    user_node_table_lock.release()
    return
    
  return

#processes VerifyAddressReply packets
#VerifyAddressReply <ip_address> <address_port> <validity> <public_key> <timestamp> <signature>
def cncclient_process_verify_address_packet(remoteIP, remoteport, message):
  #parse the reply
  parsed_data = message.split()
  
  #if the number of tokens in the message is incorrect, return and ignore the message after logging
  if (len(parsed_data) < 7):
    write_to_log("VerifyAddressReply message is in incorrect format, message = "+message)
    return
  
  message_part, signature_part = message.rsplit(' ',1)
  data, publickey_str, timestamp = message_part.rsplit(' ',2)
  
  #check public key in message
  message_public_key_str = publickey_str.replace('#',' ')
  message_public_key = rsa_string_to_publickey(message_public_key_str)
  
  if(not(message_public_key in cncclient_context["update_query_server_dict"].values())):
    #public keys dont match
    write_to_log("message public key -" + message_public_key_str+ "- was not found in update_query_server_dict")
    
    #message cannot be trused, so return
    return

  #check the timestamp
  valid, reason = cncSignData_checktimestamp(timestamp, PACKET_EXPIRATION_INTV)
  if not(valid):
    write_to_log("timestamp check failed: " + reason + " message="+ message)
    return
    
  #check the signature
  signature_correct = cncSignData_check_signature(message_part, signature_part, message_public_key)
  if not(signature_correct):
    write_to_log("signature check failed on VerifyAddressReply packet: " + message)
    return
    
  
  #packet is valid, so we can process it
  
  validity = parsed_data[3]
  
  #if the address is valid, add it to the cache
  if(validity == "True"):
    user_key = parsed_data[4]
    address=parsed_data[1]
    port = int(parsed_data[2])
  
    #we do not need to keep track of the port, since we never forward updates to addresses that are only obtained from verifyAddress replies
    add_address_to_cache(address, port, float(timestamp))
    
  else:
    #if the address is invallid do nothing for now
    #if a user keeps trying to contact an invallid address, he/she will get repeating cahce misses
    pass
  
  return
  

#processes AddressListUpdate packets
def cncclient_process_update_packet(remoteIP, remoteport, message):
  #parse the reply
  parsed_data = message.split()
  
  #if the number of tokens in the message is incorrect, return and ignore the message after logging
  if (len(parsed_data) < 7):
    write_to_log("address list message is in incorrect format, message = "+message)
    return
  
  message_part, signature_part = message.rsplit(' ',1)
  data, publickey_str, timestamp = message_part.rsplit(' ',2)
  
  #check public key in message
  message_public_key_str = publickey_str.replace('#',' ')
  message_public_key = rsa_string_to_publickey(message_public_key_str)
  
  if(not(message_public_key in cncclient_context["update_query_server_dict"].values())):
    #public keys dont match
    write_to_log("message public key -" + message_public_key_str+ "- was not found in update_query_server_dict")
    
    #message cannot be trused, so return
    return
    
  #check the signature
  signature_correct = cncSignData_check_signature(message_part, signature_part, message_public_key)
  if not(signature_correct):
    write_to_log("signature check failed on AddressListUpdate packet: " + message)
    return
    
  #get the userkey form the packet
  userkey = parsed_data[1]
  
  #make sure we have a matching local userkey
  userkey_list = get_userkey_list()
  if not(userkey in userkey_list):
    #we do not have a matching local userkey, so ignore the packet
    return
  
  #check the timestamp, note for this check, we apply the packet if the timestamp is after the timestamp of teh last packet taht was applied.
  float_timestamp = float(timestamp)
  if ( (userkey in last_update_processed.keys()) and (float_timestamp <= (last_update_processed[userkey] +.1)) ):
    #return and do not apply or forward the update
    return
  
  #also, if the update is very old, regardless of what the timestamp of the last update processed was, we ignore it
  valid, reason = cncSignData_checktimestamp(timestamp, UPDATE_PACKET_EXPIRATION_INTV)
  if not(valid):
    write_to_log("timestamp check failed on update packet: " + reason + " message="+ message)
    return
  
  write_to_log("processing update packet from " + str(remoteIP))
  #the packet is valid, so now we can apply the changes it describes.
  #first, update last_update_processed[userkey] to the new update's timestamp
  last_update_processed[userkey] = float_timestamp
  
  
  #process the elements that need to be added
  if(parsed_data[2]!="None"):
    ip_port_fragments = parsed_data[2].split(',')
    
    for address_str in ip_port_fragments:
      ip_str, port_str = address_str.split(':')
      port = int(port_str)
      
      #we need to add this address to user_node_table if it is not already present
      add_address_to_cache(ip_str, port, float_timestamp, userkey)
      
  #process the elements that need to be deleted
  if(parsed_data[3]!="None"):
    ip_port_fragments = parsed_data[3].split(',')
    
    for address_str in ip_port_fragments:
      ip_str = (address_str.split(':'))[0]
      
      #if no set exists for the current userkey, we dont need to remove anything, so we are done
      if not(userkey in user_node_table.keys()):
        continue
        
      #if the address is not in the table, we dont need to do anything
      if not(ip_str in user_node_table[userkey]):
        continue
      
      #ip address must be in the table, so remove it
      user_node_table_lock.acquire()
      
      user_node_table[userkey].remove(ip_str)
      write_to_log(str(ip_str) + " removed from node cache for userkey " + str(userkey) + ", by reason updatepacket")
      
      
      #we are done with this address, so release the lock
      user_node_table_lock.release()    
      
      
  #we are done processing the update packet
  #we now need to forward it to other nodes that have the appropriate userkey
  cncclient_forward_update_packet(message, userkey)
  return

  
#forwards the given update pakcet message to nodes that have the userkey value specified.
#NUM_FORWARDING_ADDRESSES tells the number of addreses we shoudl forward to if possible
def cncclient_forward_update_packet(message, userkey):
  #we can get the ports to which to send the message from address_info_table
  
  #we need the lock to make sure the state of the data does not change while we set up the addreses to forward the update to
  user_node_table_lock.acquire()
  address_list = list(user_node_table[userkey])
  
  target_addresses = []
  
  while len(target_addresses)<NUM_FORWARDING_ADDRESSES :
    #if we have no more addresses to try, break
    if len(address_list)==0:
      break;
  
    #pick an index randomly
    r = random_randint(0,len(address_list)-1)
    
    address_to_try = address_list.pop(r)
    
    #if the address is expired, skip it and continue
    expiration, port = address_info_table[address_to_try]
    if (expiration < time_gettime()):
      continue;
    
    else:
      #add the address to list of addresses that will get an update sent to
      address_to_add = address_to_try,port
      target_addresses.append(address_to_add)
      
  #we have finished assembling the list of addresses to send the update to, so release the lock
  user_node_table_lock.release()
  
  #now for each address in target_addresses, we want to send the update packet to it
  for target_address in target_addresses:
    sendmess(target_address[0], target_address[1], message, localip=getmyip(), localport=cncclient_context["client_con_port"])
  
  return
  
#UDP listener function
#listens to incoming UDP messages on the client port and processes them
def cncclient_upd_packet_handler(remoteIP, remoteport, message, commhandle):
  #parse the reply
  parsed_data = message.split()
  
  #check if the message is a reply to a get address list request
  if parsed_data[0]=="UserKeyNotFound" or parsed_data[0]=="GetAddressesReply" :
    #call the processing function
    cncclient_process_address_list_message(remoteIP, remoteport, message)
  
  #check if message is of type GetUserKeyRangeTablesReply
  elif parsed_data[0]=="GetUserKeyRangeTablesReply":
    cncclient_context["keyrange_tables_reply"]= (message,remoteIP, remoteport)
  
  #check if the message is a reply to a renew registration request
  elif parsed_data[0]=="RenewAddressRequestComplete" or parsed_data[0]=="RenewFailedInvalidRenewalKey" :
    #store the data
    cncclient_context['renewal_request_reply'] = message
  
  #check if we received an update packet
  elif parsed_data[0]=="AddressListUpdate":
    cncclient_process_update_packet(remoteIP, remoteport, message)
  
  #check if we received a verifyAddress reply packet
  elif parsed_data[0]=="VerifyAddressReply":
    cncclient_process_verify_address_packet(remoteIP, remoteport, message)
    
  #otherwise, we have an unrecognized packet
  else:
    write_to_log("Uexpected packet received: " + message)
    
    
#main method, starts the registration event sequence for each user key and  
#starts the event sequence that updates the node list for each user key
def cncclient_initialize(port):
  cncclient_context["client_con_port"] = port

  #update the current time
  time_updatetime(port)
  sleep(5) #wait to make sure port is freed
  
  #initialize reg_server_dict and update_query_server_dict
  cncclient_context["reg_server_dict"] = cncFileParser_read_server_list_file(REGISTRATION_SERVER_FILE)
  cncclient_context["update_query_server_dict"] = cncFileParser_read_server_list_file(UPDATE_SERVER_FILE)
  
  #set up the list of registration servers.
  cncclient_context["registration_server_list"] = cncclient_getRegistrationServerList()
  
  #select and set a registration server address
  cncclient_reset_registration_server_address()
  
  #start an event sequence that maintains the list of user keys
  
  #start the packet listener
  write_to_log("starting the UDP packet listener")
  recvmess(getmyip(), cncclient_context["client_con_port"], cncclient_upd_packet_handler)
  
  #start the registration sequence
  write_to_log("starting the registration event sequence")
  cncclient_maintain_registration()

  #update the key rage and query tables
  cncclient_update_key_range_and_query_tables()
  
  #start the full address list query sequence
  write_to_log("starting the full address list query event sequence")
  settimer(0,cncclient_address_list_query,[])
  
  #start expired addresses cleanup sequence
  write_to_log("starting expired addresses cleanup sequence")
  settimer(0,cncclient_cleanup_address_info_table,[])
    
  #initialize function is complete.
#end include cncclient.repy

NEIGHBOR_INFO_FILE_NAME = "neighboripportlist.txt"

# send a probe message to each neighbor
def probe_neighbors():
  print "probing neighbors, " + str(len(mycontext["neighborlist"])) + " items in list"
  print str(mycontext["neighborlist"])
  for neighbor in mycontext["neighborlist"]:
    neighborip, neighborport = neighbor
    mycontext['sendtime'][neighbor] = getruntime()
    
    try:
      cnc_sendmess(neighborip, neighborport, 'ping',getmyip(), mycontext['myport'])
    except CncCacheMissException, e:
      #cncclient will log cache misses so we can just pass
      pass
    
    localvessel = getmyip(), mycontext['myport']
    sendmess(neighborip, neighborport,'share'+encode_row(localvessel, mycontext["neighborlist"], mycontext['latency'].copy()),getmyip(), mycontext['myport'])
    # sleep in between messages to prevent us from getting a huge number of 
    # responses all at once...
    sleep(.5)

  # Call me again in 10 seconds
  while True:
    try:
      settimer(10,probe_neighbors,[])
      return
    except Exception, e:
      if "Resource 'events'" in str(e):
        # there are too many events scheduled, I should wait and try again
        sleep(.5)
        continue
      raise
  


# Handle an incoming message
def got_message(srcip,srcport,mess,ch):
  src_ipport_pair = srcip, srcport
  if mess == 'ping':
    try:
      cnc_sendmess(srcip,srcport,'pong', getmyip(), mycontext['myport'])
    except CncCacheMissException, e:
      #cncclient will log cache misses so we can just pass
      pass
    
  elif mess == 'pong':
    # elapsed time is now - time when I sent the ping
    mycontext['latency'][src_ipport_pair] = getruntime() - mycontext['sendtime'][src_ipport_pair]

  elif mess.startswith('share'):
    mycontext['row'][src_ipport_pair] = mess[len('share'):]



def encode_row(row_ipport_pair, neighborlist, latencylist):

  retstring = "<tr><td>"+row_ipport_pair[0] + ":" + str(row_ipport_pair[1]) +"</td>"
  for neighbor in neighborlist:
    neighborip, neighborport= neighbor
    if neighbor in latencylist:
      retstring = retstring + "<td>"+str(latencylist[neighbor])[:4]+"</td>"
    else:
      retstring = retstring + "<td>Unknown</td>"

  retstring = retstring + "</tr>"
  return retstring


# Displays a web page with the latency information
def show_status(srcip,srcport,connobj, ch, mainch): 

  webpage = "<html><head><title>Latency Information</title></head><body><h1>Latency information from "+getmyip()+' </h1><table border="1">'
  
  #get a string representation of each neighbor
  neighborstringlist=[]
  for neighborip, neighborport in mycontext['neighborlist']:
    neighborstringlist.append(neighborip+":"+str(neighborport))  
  
  webpage = webpage + "<tr><td></td><td>"+ "</td><td>".join(neighborstringlist)+"</td></tr>"

  # copy to prevent a race
#  connobj.send(encode_row(getmyip(), mycontext['neighborlist'], mycontext['latency'].copy()))

  for nodeip, nodeport in mycontext['neighborlist']:
    node_ipport_pair = nodeip, nodeport
    if node_ipport_pair in mycontext['row']:
      webpage = webpage + mycontext['row'][node_ipport_pair]+'\n'
    else:
      webpage = webpage + '<tr><td>'+nodeip + ":" + str(nodeport) +'</td><td>No Data Reported</td></tr>\n'

  # now the footer...
  webpage = webpage + '</table></html>'

  # send the header and page
  connobj.send('HTTP/1.0 200 OK\nContent-Length: '+str(len(webpage))+'\nDate: Fri, 31 Dec 1999 23:59:59 GMT\nContent-Type: text/html\n\n'+webpage) 

  # and we're done, so let's close this connection...
  connobj.close()



if callfunc == 'initialize':

  # this holds the response information (i.e. when nodes responded)
  mycontext['latency'] = {}

  # this remembers when we sent a probe
  mycontext['sendtime'] = {}

  # this remembers row data from the other nodes
  mycontext['row'] = {}
  
  # get the nodes to probe
  #used to store neighbor ip,port pairs
  mycontext['neighborlist'] = []
  
  f = open(NEIGHBOR_INFO_FILE_NAME, mode='r')
  for line in f:
    raw_data = line.strip()
    ip, port_str = raw_data.split()
    port = int(port_str)
    vessel_entry = ip, port
    mycontext['neighborlist'].append(vessel_entry)
  f.close()

  ip = getmyip() 
  if len(callargs) != 1:
    raise Exception, "Must specify the port to use for cnc communcation"
  mycontext['cncport']= int(callargs[0])
  
  #we need to use the port assigned to this address in the NEIGHBOR_INFO_FILE_NAME file'
  pingport = None
  for ip_search, port_search in mycontext['neighborlist']:
    if ip_search==ip:
      pingport = port_search
      break
  
  mycontext['myport']=pingport
  
  #get necessary cncclient data and register with cnc servers
  cncclient_initialize(mycontext['cncport'])
  sleep(10)
  
  # call gotmessage whenever receiving a message
  recvmess(ip,pingport,got_message)  

  probe_neighbors()

  # we want to register a function to show a status webpage (TCP port)
  pageport = pingport
  #waitforconn(ip,pageport,show_status)  


