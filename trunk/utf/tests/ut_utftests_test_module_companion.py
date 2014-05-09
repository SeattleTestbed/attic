"""
Makes sure that module-level companion scripts do not get run twice.
See: https://seattle.poly.edu/ticket/1384#comment:6
"""

import subprocess
import sys

process = subprocess.Popen([sys.executable, 'utf.py', '-m', 'stagedtestsetup'],
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)

(out, err) = process.communicate()

# Newlines on windows are represented as \r\n, whereas on Unix-like
# systems they are \n.  Let's make all newlines \n to reduce headaches.
out = out.replace('\r\n', '\n')

expected_output = open('utftests_module_companion_output.txt').read()
if out != expected_output:
  print "Output does not match expected output!"
  print "Generated output:"
  print out
if err:
  print err
