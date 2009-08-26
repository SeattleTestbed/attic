"""
<Program Name>
  Random_resource.py

<Started>
  March 25, 2009

<Author>
  Anthony Honstain

<Purpose>
  Benchmark the time required to generate random bytes using os.urandom.
  
    
"""
import os
import time

class InvalidTimeMeasurementError(Exception):
  pass


def urandom_measurement(bytes):
  """
  <Purpose> 
    Measure the time required to generate the requested number of bytes.

  <Arguments>
    bytes:
           The number of random bytes to request.

  <Exceptions>
    NotImplementedError if os.urandom is unable to find a OS specific
    source of randomness.

  <Side Effects>
    None. 

  <Returns>
    Float that represents the time required for the bytes to be collected.
  """   
    
  #Measure time to generate
  start = time.time()
  result = os.urandom(bytes)
  runtime = time.time() - start
  
  return runtime


def measure_random():
  """
  <Purpose>
    Run the benchMark function the designated number of times and use the
    float value returned to calculate the median and standard deviation.
  
  <Arguments>
    None
 
  <Side Effects>
    Makes a call to OS specific random number generator.

  <Exceptions>
    InvalidTimeMeasurementError:
        The system may generate numbers much faster than its clock
        has granularity, this is an attempt to indicate more about the 
        problem than just letting a division by zero exception propogate.
        
  <Returns>
    The bytes per second that random numbers were generated. Result is of 
    type Float.
  """  

  # 7 is the smallest number of bytes that can be called from urandom
  # and any time.
  num_of_bytes = 7 
  num_of_tests = 20

  data = []

  # Fallback start time, in case OSRNG is to fast for time.time()
  starttime = time.time()
  
  for i in range(num_of_tests):
    result = urandom_measurement(num_of_bytes)  
    data.append(result)
  
  # This will be used in the event no data was gathered from individual
  # tests
  totaltime = time.time() - starttime

  # Attempt to get the median
  data.sort()
  median = data[len(data)/2]

  
  # On some systems the time measurement may be to inaccurate to measure
  # at this scale. Will try several ways to get valid data:
  #   1) Will use the median, if that fails
  #   2) will use the max, if that fails
  #   3) will use the time required for the entire test, if that fails
  #   4) will raise an exception and the test will have failed.
  if median != 0.0:
    return int(num_of_bytes/median) 
  
  elif data[-1] != 0.0:
    # use the maximum time required for a single os.urandom call
    return int(num_of_bytes/data[-1])
  
  elif totaltime != 0.0:
    # No useful time measurement was taken for an individual tests,
    # so we will use the time required to perform the entire test.
    return int((num_of_bytes * num_of_tests) / totaltime)
  
  else:
    # The number of tests per time measurement should be increased.
    # Will require that num_of_bytes or num_of_tests be increased.
    raise InvalidTimeMeasurementError("os.urandom generated bytes to quickly for valid time measurement") 


if __name__ == "__main__":
  print measure_random()
    

  
  
