#!/bin/bash
#
# Runs the tests
# Takes 1 optional parameter: class
# If class parameter is given, then only test_CLASS_*.py will be run

# Go into the built dir
cd built

# Clean old logs
LOGCOUNT=`ls log/ | grep -c ""`
if [ ${LOGCOUNT} -gt "0" ]
then
  echo "Archiving old logs..."
  DATE=`date +%s`
  NAME=logs.${DATE}.tar
  tar -cf ${NAME} log/*
  echo "Created Archive: ${NAME}"
  echo "Clearing old logs..."
  rm -f ./log/*
fi

# Stop the old forwarder if it is running
if [ -f run/forwarder.pid ]
then
  echo "Stopping old forwarder..."
  ./scripts/stop_forwarder.sh
fi

echo "Starting forwarder..."
./scripts/start_forwarder.sh

# Sleep for a second, give the forwarder a change to start
echo "Waiting for forwarder to initialize..."
sleep 5

forwarderpid=`cat ./run/forwarder.pid`

# Check if the forwarder is still running
forwarderstat=`ps -p ${forwarderpid} | grep -c ""`
if [ ${forwarderstat} -eq "1" ]
then
      echo "Fatal Error! Forwarder has not started!"
      rm ./run/forwarder.pid
      exit
fi

# Pre-process each file
echo "Running tests..."
echo "#####"

# Run only selected test "class" if there is a parameter
if [ $# -gt "0" ]
then
  all_tests=`ls test_$1_*.py`
else
  all_tests=`ls test_*.py`
fi

for f in ${all_tests}
do
  printf "Running %-60s" ${f}
  
  # Log the output
  run="python repy.py --logfile log/${f}.log restrictions.default ${f}"
  ${run}  >/dev/null 2>&1 &
  
  # Wait for that to finish
  wait 2>/dev/null
   
  # Check if the log size is 0
  size=`cat ./log/${f}.log.old | grep -c ''`
  if [ ${size} -eq "0" ]
  then
    printf "[ PASSED ]\n"
  else
    printf "[ FAILED ]\n"
  fi
  
  # Sleep for a second
  sleep 1
  
  # Check if the forwarder is still running
  forwarderstat=`ps -p ${forwarderpid} | grep -c ""`
  if [ ${forwarderstat} -eq "1" ]
  then
      echo "Fatal Error! Forwarder Dead!"
      exit
  fi
done

echo "#####"
echo "Done!"

# Start the forwarder
echo "Stopping forwarder!"
./scripts/stop_forwarder.sh
