"""
Makes sure that setup, subprocess and shutdown scripts without a base
test do not get skipped.  See #1384.
"""

# utf will print out the names of the tests if they get run.
# since the modules there is no test with the name
# ut_stagedtestnobase_test.py, they must be executed in this order.
#pragma out Running: ut_stagedtestnobase_test_setup.py
#pragma out Running: ut_stagedtestnobase_test_shutdown.py
#pragma out Running: ut_stagedtestnobase_test_subprocess.py

import subprocess
import sys

process = subprocess.Popen([sys.executable, 'utf.py', '-m', 'stagedtestnobase'],
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)

(out, err) = process.communicate()

if out:
  print out
if err:
  print err
