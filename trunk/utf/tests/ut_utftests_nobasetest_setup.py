"""
Make sure the nobasetest runs without a file with the base filename in
the current directory.  See #1384.
"""

import os

try:
  os.remove('ut_stagedtestnobase_test.py')
except OSError:
  pass
