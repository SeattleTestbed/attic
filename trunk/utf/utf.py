#!/usr/bin/python
"""
<Program>
  Seattle Test Framework


<Author>
  Vjekoslav Brajkovic
  Stephen Sievers

<Started>
  2009-07-11


<Requirements>

  <Naming Convention>

    Required naming convention for every test file:

    ut_MODULE{_DESCRIPTOR].py

    There can be multiple descriptors associated with a module.

    <Example>
      ut_semaphore_simple_create.py
      ut_semaphore_simple_destroy.py

  <Pragma Directives>

    The token-string is a series of characters that gives a specific framework
    instruction and arguments, if any. The number sign (#) must be the first
    non-white-space character on the line containing the pragma; white-space
    characters can separate the number sign and the word pragma. Following
    #pragma, write any text that the translator can parse as preprocessing
    tokens.

    <Example>
      #pragma repy [RESTRICTIONS]
      #pragma out [TEXT]
      #pragma error [TEXT]

    The parser throws an exception on unrecognized pragmas.

<Modified>
  Modified on Nov. 16, 2010 by Monzur Muhammad to add functionality for the
  verbose option. Now if verbose is on, it display the time taken for the test.
"""


import glob
import optparse
import os
import signal
import subprocess
import sys
import time

import utfutil

# Valid prefix and suffix.
SYNTAX_PREFIX = 'ut_'
SYNTAX_SUFFIX = '.py'


COMPANION_SETUP = 'setup'
COMPANION_SHUTDOWN = 'shutdown'
COMPANION_SUBPROCESS = 'subprocess'


# Acceptable pragma directives.
REPY_PRAGMA = 'repy'
ERROR_PRAGMA = 'error'
OUT_PRAGMA = 'out'


# Verbose Option
VERBOSE = False

SHOW_TIME = False

# UTF Exceptions.
class InvalidTestFileError(Exception):
  pass
class InvalidPragmaError(Exception):
  pass




def main():
  """
  <Purpose>
    Executes the main program that is the unit testing framework.
    Tests different modules, files, capabilities, dependent on command
    line arguments.

  <Arguments>
    None

  <Exceptions>
    None.

  <Side Effects>
    None

  <Returns>
    None
  """
  ###
  ### Define allowed arguments.
  ### Update ut_utftests_utf.py with the changes in Options list
  ###
  parser = optparse.OptionParser()

  ### Generic Option Category.
  group_generic = optparse.OptionGroup(parser, "Generic")

  # Verbose flag.
  group_generic.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="verbose output")

  # Verbose flag.
  group_generic.add_option("-T", "--show-time",
                    action="store_true", dest="show_time", default=False,
                    help="display the time taken to execute a test.")

  parser.add_option_group(group_generic)

  ### Testing Option Category.
  group_test = optparse.OptionGroup(parser, "Testing")

  # Test for a specific module.
  group_test.add_option("-m", "--module", dest="module",
                        help="run tests for a specific module",
                        metavar="MODULE")

  # Run a specific test file.
  group_test.add_option("-f", "--file", dest="file",
                        help="execute a specific test file",
                        metavar="FILE")

  # Run all tests in current directory
  group_test.add_option("-a", "--all", dest="all", action="store_true",
                        help="execute all test files",
                        metavar="ALL")

  parser.add_option_group(group_test)

  # All files in the current working directory.
  all_files = glob.glob("*")

  # Sort so that it is easier to keep track if a test passed/failed.
  all_files.sort()

  # Valid test files in the current working directory.
  valid_files = filter_files(all_files)

  ###
  # Parse the arguments.
  ###
  (options, args) = parser.parse_args()


  #Count number of args for legal number of args test
  i = 0
  if (options.module):
    i = i + 1
  if (options.all):
    i = i + 1
  if (options.file):
    i = i + 1

  # Test for mutual exclusion.
  if i > 1:
    parser.error("Options are mutually exclusive!")


  # Check if the show_time option is on.
  if (options.show_time):
    global SHOW_TIME
    SHOW_TIME = True


  if (options.file): # Single file.

    file_path = options.file

    # I need to derive the module name...
    if not file_path.startswith('ut_') or len(file_path.split('_'))<3:
      print "Error, cannot determine module name from filename '"+file_path+"'"
      return
    else:
      module_name = file_path.split('_')[1]

    # the test_module code is really poorly structured.   I need to tell it to
    # consider the shutdown, setup, and subprocess scripts...
    files_to_use = [file_path]
    module_file_list = filter_files(valid_files, module = module_name)

    files_to_use = files_to_use + filter_files(module_file_list, descriptor = 'setup')
    files_to_use = files_to_use + filter_files(module_file_list, descriptor = 'shutdown')
    files_to_use = files_to_use + filter_files(module_file_list, descriptor = 'subprocess')

    test_module(module_name, files_to_use)

  elif (options.module): # Entire module.

    # Retrieve the module name.
    module_name = options.module

    module_file_list = filter_files(valid_files, module = module_name)

    # is the module empty? we should print something to indicate this is likely
    # an error...
    if len(module_file_list) == 0:
      print "No module with name:",module_name
      return

    test_module(module_name, module_file_list)

  elif (options.all): #all test files
    test_all(valid_files)

  else: # If no options are present, print the usage
    parser.print_help()




def execute_and_check_program(file_path):
  """
  <Purpose>
    Given the test file path, this function will execute the program and
    monitor its behavior

  <Arguments>
    Test file path.

  <Exceptions>
    None.

  <Side Effects>
    None

  <Returns>
    None
  """
  file_path = os.path.normpath(file_path)
  testing_monitor(file_path)





def test_file(file_path, script_files):
  """
  <Purpose>
    Run tests on file_path. If  setup, shutdown, or subprocess scripts exist for the 
    file_path, they will be taken from the script_files list, and run as well

  <Arguments>
    file_path: The ut file to be tested
    script_files: A list of setup, shutdown, and subprocess files in the module

  <Exceptions>
    None

  <Side Effects>
    None

  <Returns>
    None
  """
  # Grabs the individual components of the file_path, and removes
  # the extension(.py) from the last componenet
  components = file_path.split('_')
  components[-1] = components[-1].split('.')[0]

  setup_file = None
  subprocess_file = None
  shutdown_file = None

  for filename in script_files:
    script_type = get_script_type(filename, script_files)
    if script_type == COMPANION_SETUP:
      setup_file = filename
    elif script_type == COMPANION_SUBPROCESS:
      subprocess_file = filename
    elif script_type == COMPANION_SHUTDOWN:
      shutdown_file = filename

  sub = None
  # If we must open a process to run concurrently with the tests, we will use
  # its stdin to indicate when to stop...
  if subprocess_file:
    script_files.remove(subprocess_file)
    print "Now starting subprocess: " + subprocess_file
    sub = subprocess.Popen([sys.executable, subprocess_file], stdin=subprocess.PIPE)
    # Give the process time to start
    time.sleep(30)

  if setup_file:
    script_files.remove(setup_file)
    execute_and_check_program(setup_file)

  execute_and_check_program(file_path)

  if shutdown_file:
    script_files.remove(shutdown_file)
    execute_and_check_program(shutdown_file)

  #If we opened a subprocess, we need to stop it by shutting its stdin
  if sub:
    print "Now stopping subprocess: " + subprocess_file
    sub.stdin.close()
    sub.wait()





def test_module(module_name, module_file_list):
  """
  <Purpose>
    Execute all test files contained within module_file_list matching the
    module_name in the form of each test file name 'ut_<module_name>_<descriptor>.py'

  <Arguments>
    module_name: module name to be tested
    module_file_list: a list of files to be filtered by module name and ran through
      the testing framework

  <Exceptions>
    None

  <Side Effects>
    None

  <Returns>
    None
  """
  print 'Testing module:', module_name

  setup_file = None

  # Given all test files for the specified module name, find the file whose
  # descriptor equals 'setup' (there can be only one such file name).
  filtered_files = filter_files(module_file_list, descriptor = 'setup')

  if filtered_files:
    setup_file = filtered_files.pop()
    module_file_list.remove(setup_file)

  subprocess_file = None

  filtered_files = filter_files(module_file_list, descriptor = 'subprocess')
  if filtered_files:
    subprocess_file = filtered_files.pop()
    module_file_list.remove(subprocess_file)

  shutdown_file = None

  # Given all test files for the specified module name, find the file whose
  # descriptor equals 'shutdown' (there can be only one such file name).

  filtered_files = filter_files(module_file_list, descriptor = 'shutdown')
  if filtered_files:
    shutdown_file = filtered_files.pop()
    module_file_list.remove(shutdown_file)


  sub = None
  # If we must open a process to run concurrently with the tests, we will use
  # its stdin to indicate when to stop...
  if subprocess_file:
    print "Now starting subprocess: " + subprocess_file
    sub = subprocess.Popen([sys.executable, subprocess_file], stdin=subprocess.PIPE)
    # Give the process time to start
    time.sleep(30)

  if setup_file:
    print "Now running setup script: " + setup_file
    execute_and_check_program(setup_file)

  # test_file() is responsible for running companion tests.
  # We shouldn't run them directly.
  all_module_files = filter_files(module_file_list, module=module_name)
  all_test_files = all_module_files[:]
  for mod_file in all_module_files:
    if get_script_type(mod_file, all_module_files) is not None:
      all_test_files.remove(mod_file)

  start_time = time.time()

  # Run the module tests
  for file_path in all_test_files:
    test_file(file_path, module_file_list)

  end_time = time.time()


  if shutdown_file:
    print "Now running shutdown script: " + shutdown_file
    execute_and_check_program(shutdown_file)

  #If we opened a subprocess, we need to stop it by shutting its stdin
  if sub:
    print "Now stopping subprocess: " + subprocess_file
    sub.stdin.close()
    sub.wait()


  if SHOW_TIME:
    print "Total time taken to run tests on module %s is: %s" % (module_name, str(end_time-start_time)[:6])




def test_all(file_list):
  """
  <Purpose>
    Given the list of valid test files, this function will test each module
    within the test file list

  <Arguments>
    file_list: List of test files to be ran

  <Exceptions>
    None

  <Side Effects>
    None

  <Returns>
    None
  """
  module_dictionary = { }

  # Map test files to their respective modules.
  # dictionary[module name] -> list(test files)
  for test_file in file_list:
    (module, descriptor) = parse_file_name(test_file)

    if module_dictionary.has_key(module):
      module_dictionary[module].append(test_file)
    else:
      module_dictionary[module] = [test_file]

  # Test each module.
  for module_name, module_file_list in module_dictionary.iteritems():
    test_module(module_name, module_file_list)




def testing_monitor(file_path):
  """
  <Purpose>
    Executes and prints the results of the unit test contained within 'file_path'


  <Arguments>
    file_path: File to be used within the testing_monitor

  <Exceptions>
    InvalidPragmaError: if there is an invalid pragma within the source file

  <Side Effects>
    None

  <Returns>
    None
  """

  # Source the file.
  file_object = open(file_path)
  source = file_object.read()

  (tail, head) = os.path.split(file_path)

  (module, descriptor) = parse_file_name(head)
  print "\tRunning: %-50s" % head,
  # flush output in case the test hangs...
  sys.stdout.flush()

  # Parse all pragma directives for that file.
  try:
    pragmas = parse_pragma(source)
  except InvalidPragmaError:
    print '[ ERROR ]'
    print_dashes()
    print 'Invalid pragma directive.'
    print_dashes()

    return

  # Now, execute the test file.
  start_time = time.time()
  report = execution_monitor(file_path, pragmas)

  # Calculate the time taken for the test
  end_time = time.time()
  time_taken = str(end_time - start_time)[:5]
  if len(time_taken) < 5:
    time_taken = " "*(5-len(time_taken)) + time_taken

  if report:
    if SHOW_TIME:
      print '[ FAIL ] [ %ss ]' % time_taken

    else:
      print '[ FAIL ]'



    print_dashes()

    for key, value in report.items():
      print 'Standard', key, ':'
      produced_val, expected_val = value
      print "."*30 + "Produced" + "."*30 + "\n" + str(produced_val)
      print "."*30 + "Expected" + "."*30 + "\n" + str(expected_val)
      print_dashes()

  else:
    if SHOW_TIME:
      print '[ PASS ] [ %ss ]' % time_taken
    else:
      print '[ PASS ]'




def execution_monitor(file_path, pragma_dictionary):
  """
  <Purpose>
    Executes a unit test written with a source contained in file_path. If the source
    contains any pragmas (#pragma out, #pragma repy, #pragma err), the unit testing
    framework creates the report differently. If there is a repy pragma, the test
    executes in repy, not python. If there is an out or err pragma, the unit testing
    framework will include that there was to be output in the report.

  <Arguments>
    file_path: file to be executed under the framework
    pragma_dictionary: dictionary of pragmas within this test file

  <Exceptions>
    None

  <Side Effects>
    None

  <Returns>
    A report containing information about any unexpected output:
    { Pragma Type : (Produced, Expected), ... }
  """

  # Status report.
  report = { }

  executable = sys.executable
  popen_args = [ executable ]

  if pragma_dictionary.has_key(REPY_PRAGMA):
    repy = 'repy.py'
    default_restriction = 'restrictions.default'

    # Did the user specify a non-default restrictions file?
    repyArgs = pragma_dictionary[REPY_PRAGMA]
    if not repyArgs:
      repyArgs = default_restriction

    popen_args.append(repy)

    # For tests requiring repy arguments besides restrictions.default
    # the user must specify them after the pragma
    arguments = repyArgs.split(" ")
    for element in arguments:
      popen_args.append(element)

  popen_args.append(file_path)

  # Execute the program.
  (out, error) = utfutil.execute(popen_args)

  report = {}

  verify_results(OUT_PRAGMA, pragma_dictionary, out, report)
  verify_results(ERROR_PRAGMA, pragma_dictionary, error, report)


  return report





def verify_results(pragma_type, pragma_dictionary, output, report):
  '''
  <Purpose>
    Checks output to ensure that what is expected to be printed to the screen
    has been printed.

  <Arguments>
    pragma_type: string
      A token indicating which pragma to check.
    pragma_dictionary: dict
      The pragma_dictionary generated by parse_pragma()
    output: string
      This should be the contents of stdout or stderr.
    report:
      A dictionary to store the report in.  This value will be modified.

  <Side Effects>
    If an expected string is not found in the given output string, a tuple
    corresponding to the current pragma will be added to the report, in the
    form: (expected output, actual output).

  <Exceptions>
    InvalidPragmaError:
      The specified pragma already exists in the report.  This indicates an
      internal error with the UTF.

  <Return>
    None

  '''

  # Check to make sure this report does not already exist.
  # This is to ensure we don't mask any bugs.
  if pragma_type in report:
    raise InvalidPragmaError("Pragma already exists in report")

  # Standardize newlines
  out = output.replace('\r\n', '\n')

  # Get rid of an escape sequence that Mac's readline prints out on import. #1110
  # I'm assuming this will only occur at the very beginning of stdout. Possible bug?
  # Should we also do this for the stderr?
  escape_sequence = '\x1b[?1034h'
  if out.startswith(escape_sequence):
    out = out[len(escape_sequence):]

  # Get rid of debug output on Android, #1084.
  out = strip_android_debug_messages(out)

  # Is this executable suppose to produce any output on standard out?
  if pragma_dictionary.has_key(pragma_type):
    outlines = out.split('\n')
    expected_out_lines = pragma_dictionary[pragma_type]

    # Preserve the original
    remaining_out_lines = expected_out_lines[:]

    for outline in outlines:
      # Are there any wildcards?
      # We use '' to indicate wildcards.
      while remaining_out_lines and not remaining_out_lines[0]:
        remaining_out_lines = remaining_out_lines[1:]

      # Are there remaining expected lines?
      if remaining_out_lines and remaining_out_lines[0] in outline:
        remaining_out_lines = remaining_out_lines[1:]

    # Get rid of any remaining wildcards that may still exist
    while remaining_out_lines and not remaining_out_lines[0]:
      remaining_out_lines = remaining_out_lines[1:]

    if remaining_out_lines:
      # Mark wildcards
      expected_output = ""
      for line in expected_out_lines:
        # Don't display wildcards
        if not line:
          continue
        expected_output += line + '\n'

      report[pragma_type] = (out, expected_output)
  elif out: # If not, make sure the standard out is empty.
    report[pragma_type] = (out, None)






def parse_pragma(source_text):
  """
  <Purpose>
    Parses pragma directives which are contained within a source code file.
    Possible pragmas inside of a source code include:
      #pragma out arg
      #pragma err arg
      #pragma repy arg

  <Arguments>
    source_text: the content of a particular file

  <Exceptions>
    InvalidPragmaError: When a pragma of an unrecognizable format is used
      (i.e. none of the above)

  <Side Effects>
    None

  <Returns>
    Parsed pragma directives:
    { Pragma Type : Argument, ... }
  """
  directive  = 'pragma'
  pragma_directives = utfutil.parse_directive(source_text, directive)
  pragma_dictionary = { }

  for (directive, pragma_type, arg) in pragma_directives:
    if pragma_type == REPY_PRAGMA:
      pragma_dictionary[pragma_type] = arg

    # Only out and error pragmas are used for output checking
    elif pragma_type in (OUT_PRAGMA, ERROR_PRAGMA):
      if not pragma_type in pragma_dictionary:
        pragma_dictionary[pragma_type] = []
      pragma_dictionary[pragma_type].append(arg)

    else:
      print "Unknown pragma: ", pragma_type
      raise InvalidPragmaError(pragma_type)

  return pragma_dictionary




def parse_file_name(file_name):
  """
  <Purpose>
    Parses a file name to identify its module and its descriptor

  <Arguments>
    file_name: the name of the test file

  <Exceptions>
    InvalidTestFileError: if you provide a test file which does not follow the
      naming convention of 'ut_<module>_<descriptor>.py'

  <Side Effects>
    None

  <Returns>
    A tuple containing (module, descriptor) in the file's naming convention of
      'ut_<module>_<descriptor>.py'

  """
  if not file_name.startswith(SYNTAX_PREFIX):
    raise InvalidTestFileError(file_name)
  if not file_name.endswith(SYNTAX_SUFFIX):
    raise InvalidTestFileError(file_name)

  # Remove prefix and suffix.
  stripped = file_name[len(SYNTAX_PREFIX):-len(SYNTAX_SUFFIX)]
  # Partition the string.
  (module, separator, descriptor) = stripped.partition('_')

  # Empty module name is not allowed.
  if not module:
    raise InvalidTestFileError(file_name)

  return (module, descriptor)




def filter_files(file_list, module = None, descriptor = None):
  """
  <Purpose>
    Given the list of files 'file_list', filter out all invalid test files, that is,
    test files which do not have a module name of 'module' or a descriptor of 'descriptor'
    in the form of 'ut_<module>_<descriptor>.py.

  <Arguments>
    Module name.
    Descriptor.

  <Exceptions>
    InvalidTestFileError--Raised if you provide a test file of incorrect format
      (all files must follow name convention of ut_<module>_<descriptor>.py).

  <Side Effects>
    None

  <Returns>
    A list of all filtered file names:
    [Filtered File Name list]
  """
  result = []

  for file_name in file_list:

    try:
      (file_module, file_descrriptor) = parse_file_name(file_name)
    except InvalidTestFileError: # This is not a valid test file.
      continue

    # Filter based on the module name.
    if module and file_module != module:
      continue
    # Filter based on the descriptor.
    if descriptor and file_descrriptor != descriptor:
      continue

    result.append(file_name)

  return result




def print_dashes():
  print '-' * 80




def strip_android_debug_messages(rawoutput):
  """
  Interim fix for #1084: Get rid of stray debugging output on Android
  of the form "dlopen libpython2.6.so" and "dlopen /system/lib/libc.so",
  yet preserve all of the other output (including empty lines).

  Note that almost the same code is used in trunk/repy/safe.py as of r5639.
  """

  # Are we running on Android?
  try:
    import android
  except ImportError:
    # If not, then we are done!
    return rawoutput

  # If we are, then there is work to do (as of Py4A 2.6.2)
  output = ""
  for line in rawoutput.split("\n"):
    # Preserve empty lines
    if line == "":
      output += "\n"
      continue
    # Suppress debug messages we know can turn up
    wordlist = line.split()
    if wordlist[0]=="dlopen":
      if wordlist[-1]=="/system/lib/libc.so":
        continue
      if wordlist[-1].startswith("libpython") and \
        wordlist[-1].endswith(".so"):
        # We expect "libpython" + version number + ".so".
        # The version number should be a string convertible to float.
        # If it's not, raise an exception.
        try:
          versionstring = (wordlist[-1].replace("libpython",
            "")).replace(".so", "")
          junk = float(versionstring)
        except TypeError, ValueError:
          raise Exception("Unexpected debug output '" + line +
            "' while evaluating code safety!")
    else:
      output += line + "\n"

  # Strip off the last newline character we added
  return output[0:-1]



def get_script_type(scriptname, all_scripts):
  """
  <Purpose>
    Gets the type of a script file, in the context of all_scripts.

    There are two types of scripts, standalone unit tests and companion
    scripts.  Companion scripts are setup/shutdown/subprocess scripts
    that need to be run at specific times, that perform tasks depended
    on by other unit tests.

  <Arguments>
    scriptname:
      The name of the script to look at.

    all_scripts:
      The names of all the files in the directory that contains
      scriptname.

  <Side Effects>
    None

  <Exceptions>
    None

  <Returns>
    None if scriptname is a standalone unit test.  Otherwise, it returns
    the type of the companion script.
  """
  # Script names are in the form: ut_[module]_[test]_[companion].py
  base_name, last_filename_component = scriptname.rsplit('_', 1)

  # We're not interested in the *.py extension
  last_filename_component = last_filename_component.split('.')[0]

  # If there is no base test, then this is a standalone unit test.
  base_test_script = base_name + '.py'

  if base_test_script in all_scripts:
    # Locates and stores setup/subprocess/shutdown files, if any exist.
    for companion_type in [COMPANION_SHUTDOWN, COMPANION_SETUP, COMPANION_SUBPROCESS]:
      if last_filename_component == companion_type:
        return companion_type
  return None


if __name__ == "__main__":
  try:
    main()
  except IOError:
    raise
  except InvalidTestFileError, e:
    print 'Invalid file name syntax:', e
  except:
    print 'Internal error. Trace:'
    print_dashes()
    raise

