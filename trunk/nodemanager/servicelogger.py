"""
<Program>
  servicelogger.py

<Date Started>
  January 24th, 2008

<Author>
  Brent Couvrette
  couvb@cs.washington.edu

<Purpose>
  Module abstracting away service logging.  Other modules simply have to call
  log with the name of the log file they wish to write to, and the
  servicelogger will write their message with time and pid stamps to the
  service vessel.  init must be called before log.
"""

from repyportability import *
import os
import logging
import time

include servicelookup.repy


logfile = None
servicevessel = None

class ServiceLogError(Exception):
  pass

def get_servicevessel():
  """
  <Purpose>
    Get a service vessel directory from vesseldict. If none of the
    service vessel directory exists, create a new directory with the first
    service vessel. If there is no service vessel returned, do nothing.
    
  <Arguments>
    None
             
  <Exceptions>
    None
        
  <Side Effects>
    servicevessel will be changed to the correct vessel directory
    
  <Returns>
    None
  """

  global servicevessel
  
  ownerkey = "90828751313604138861138199375516065418794160799843599128558705100285394924191002288444206024669046851496823164408997538063597164575888556545759466459359562498107740756089920043807948902332473328246320686052784108549174961107584377257390484702552802720358211058670482304929480676775120529587723588725818443641 525084957612029403526131505174200975825703127251864132403159502859804160822964990468591281636411242654674747961575351961726000088901250174303367500864513464050509705219791304838934936387279630515658887485539659961265009321421059720176716708947162824378626801571847650024091762061008172625571327893613638956683252812460872115308998220696100462293803622250781016906532481844303936075489212041575353921582380137171487898138857279657975557703960397669255944572586836026330351201015911407019810196881844728252349871706989352500746246739934128633728161609865084795375265234146710503588616865119751368455059611417010662656542444610089402595766154466648593383612532447541139354746065164116466397617384545008417387953347319292748418523709382954073684016573202764322260104572053850324379711650017898301648724851941758431577684732732530974197468849025690865821258026893591314887586229321070660394639970413202824699842662167602380213079609311959732523089738843316936618119004887003333791949492468210799866238487789522341147699931943938995266536008571314911956415053855180789361316551568462200352674864453587775619457628440845266789022527127587740754838521372486723001413117245220232426753242675828177576859824828400218235780387636278112824686701"
  ownerinfo = ""
  
  readfileobj = open("vesseldict")
  readdata = readfileobj.read()
  readfileobj.close()
  vesseldict = (eval(readdata))
  
  service_vessels = servicelookup_get_servicevessels(vesseldict, ownerkey, ownerinfo)
  
  if service_vessels:
    found = False
    i = 0;
    while i < len(service_vessels) and (not found):
      found = os.path.isdir(service_vessels[i])
      i = i + 1
    
    if found:
      servicevessel = service_vessels[i-1]
    else:
      servicevessel = os.mkdir(service_vessels[0])
      
  return servicevessel
  

def init(logname):
  """
  <Purpose>
    Sets up the service logger to use the given logname, and the nodeman.cfg
    is in the given directory.
    
  <Arguments>
    logname - The name of the log file, as well as the name of the process lock
              to be used in the event of multi process locking
    cfgdir - The directory containing nodeman.cfg, by default it is the current
             directory
             
  <Exceptions>
    Exception if there is a problem reading from cfgdir/nodeman.cfg
    
  <Side Effects>
    All future calls to log will log to the given logfile.
    
  <Returns>
    None
  """

  global logfile, servicevessel
  
  servicevessel = get_servicevessel()
  
  if servicevessel != None:
    logfile = logging.circular_logger(servicevessel + '/' + logname, use_nanny=False)
  
  
def multi_process_log(message, logname):
  """
  <Purpose>
    Logs the given message to a log.  Does some trickery to make sure there
    no more than 10 logs are ever there. If the logfile or servicevessel is not
    set, this will do nothing.
    
  <Arguments>
    message - The message that should be written to the log.
    logname - The name to be used for the logfile.
  
  <Exceptions>
    Exception if there is a problem reading from cfgdir/nodeman.cfg or writing
    to the circular log.
      
  <Side Effects>
    The given message might be written to the log.
    
  <Returns>
    None
  """
  global servicevessel
  
  if servicevessel == None:
    servicevessel = get_servicevessel()
  
  if servicevessel == None:
    return
    
  logcount = 0
  for servicefile in os.listdir(cfgdir + '/' + servicevessel):
    if servicefile.endswith('.old'):
      # Count all the log files.  There is always a .old for every log?
      logcount = logcount + 1
      
  if logcount >= 10:
    # If there are 10 or more logfiles already present, we don't want to create
    # another.  To deal with the possibility of a time of check / time of use
    # vulnerability, I will recheck this after I write the file, and deal with
    # it then.  For simplicity we will just return in this case.  We might do
    # something fancier here later.
    return
  else:
    logfile = logging.circular_logger(cfgdir + '/' + servicevessel + '/' + logname)
    logfile.write(str(time.time()) + ':PID-' +str(os.getpid()) + ':' +
      str(message) + '\n')
    logfile.close()
    
    # Redo the check to make sure there weren't huge amounts of logs created
    # after we checked.  If so, lets delete ourselves so we don't contribute
    # to the mess.
    logcount = 0
    for servicefile in os.listdir(cfgdir + '/' + servicevessel):
      if servicefile.endswith('.old'):
        # Count all the log files.  There is always a .old for every log?
        logcount = logcount + 1
      
    if logcount >= 10:
      # Make sure we try to remove both the .old and .new files.
      try:
        # We will try our best to remove the file, but if it fails, we can't
        # do much about it.
        os.remove(cfgdir + '/' + servicevessel + '/' + logname + '.old')
      except Exception:
        pass
        
      try:
        # We will try our best to remove the file, but if it fails, we can't
        # do much about it.
        os.remove(cfgdir + '/' + servicevessel + '/' + logname + '.new')
      except Exception:
        pass


def log(message):
  """
  <Purpose>
    Logs the given text to the given log file inside the service directory. If the 
    logfile or servicevessel is not set, this will do nothing.
    
  <Argument>
    message - The message to log.
    
  <Exceptions>
    ServiceLogError if init has not been called.
    Exception if writing to the log fails somehow.
    
  <Side Effects>
    The given message is written to the circular log buffer.
    
  <Returns>
    None
  """

  if logfile == None or servicevessel == None:
    # If we don't have a current log file, lets raise an exception
    # raise ServiceLogError("init needs to be called before using the service log")
    return

  logfile.write(str(time.time()) + ':PID-' + str(os.getpid()) + 
    ':' + str(message) + '\n')
