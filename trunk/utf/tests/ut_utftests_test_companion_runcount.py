"""
Make sure we only run setup/shutdown/subprocess scripts the correct
number of times.

"""
import subprocess
import sys

process = subprocess.Popen([sys.executable, 'utf.py', '-m', 'stagedtestcompanion'],
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)

(out, err) = process.communicate()

num_run_setup = 0
num_run_subprocess = 0
num_run_shutdown = 0

for line in out.splitlines():
  if "Running: ut_stagedtestcompanion_test_setup.py" in line:
    num_run_setup += 1
  if "Running: ut_stagedtestcompanion_test_subprocess.py" in line:
    num_run_subprocess += 1
  if "Running: ut_stagedtestcompanion_test_shutdown.py" in line:
    num_run_shutdown += 1

if num_run_setup != 1:
  print "Ran setup script", num_run_setup, "times, when should be run 1 time!"

if num_run_subprocess != 0:
  print "Ran subprocess script", num_run_subprocess, "times, when should be run 0 times!"

if num_run_shutdown != 1:
  print "Ran shutdown script", num_run_shutdown, "times, when should be run 1 time!"
