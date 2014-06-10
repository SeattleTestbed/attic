# Written by Moshe Kaplan
# 2012-03-17

import re
import sys

# Allowed types: ascii, utf-8, and iso8859-* -> Based on Ned Batchelder's recommendation
def check_safe_encoding(code):
  encoding = get_encoding(code)
  return encoding in ('ascii','utf-8') or encoding.startswith('iso8859-')

# Parses a string representation of a file and returns the encoding python will use to parse the file
# Based on http://www.python.org/dev/peps/pep-0263/
def get_encoding(code):
  result = None
  # Only examine (up to) the first two lines
  for line in code.splitlines()[:2]:
    result = _examine_line(line)
    if result:
      break
  
  # The encoding type was determined from the file
  if result:
    return result
  else:
    return sys.getdefaultencoding()


# Returns the encoding read from the text, or None
def _examine_line(line):
  # Example: # -*- coding:  UTF-8 -*-
  # The encoding is the word after 'coding:'
  match = re.match(r"[ \t]*#.*?coding:[ \t]*([\w-]+)", line)
  if match:
    return match.group(1)

# Some simple tests: (to be moved to another file)
if __name__ == '__main__':
  # Pep 263 Example 1 - latin-1
  print get_encoding("	# -*- coding: latin-1 -*")

  # Pep 263 Example 2 - utf-8
  print get_encoding(" # This Python file uses the following encoding: utf-8")

  # Pep 263 Example 3 - latin-1
  print get_encoding("#!/usr/local/bin/python\n          # coding: latin-1")

  # Pep 263 Example 4 - none - ascii
  print get_encoding(" #!/usr/local/bin/python")

  # Pep 263 Example 5 - doesn't work, ascii
  print get_encoding(" # latin-1")

  # Two encodings - only the first (rot13) is used:
  print get_encoding("#coding:rot13\n#latin-1")
