"""
<Program Name>
  seash_importer.py

<Purpose>
  This is the module importer for seash. It allows developers to easily extend
  the functionality of seash without having to modify core seash files.

  The importer will expect a folder containing a file called __init__.py.
  This will be referenced here as the commanddict file. For every module, there
  must be exactly one commanddict file. Simply add this folder into the modules/
  folder, and seash will import it automatically.

  Inside the commanddict file, there should be a variable in the module scope
  named command_dict. You can define new commands in the same manner as
  described in seash_dictionary.py.

  Note, you cannot override existing commands. Attempting to do so will result
  in an error.

"""
import warnings
import seash_exceptions
import os
import sys
from copy import deepcopy

# All seash modules are subdirectories under this directory.
MODULES_FOLDER_PATH = os.path.abspath('modules')

# Stores all the imported commanddicts
module_data = {}

def import_module(modulefn):
  """
  <Purpose>
    Imports a seash module with the specified modulename.
    The seash module is treated as a python package  
    
  <Arguments>
    modulefn:
      The name of the main modules file.
      
  <Side Effects>
    The commands found in modulename, alongside the helptext for the module
    will be imported and returned.
    
  <Exceptions>
    ImportError
    
  <Return>
    A dictionary containing the command_dict and the helptext.

    An example: {
      'command_dict': {'command1': ...,'command2':...},
      'help_text': 'This is the module helpstring'
    }

  """
  # We can't import python modules by specifying the full path to the module
  # Temporarily add the module path to the pythonpath
  sys.path = [MODULES_FOLDER_PATH] + sys.path
  moduleobj = __import__(modulefn)
  try:
    _attach_module_identifier(moduleobj.moduledata['command_dict'], modulefn)
    return moduleobj.moduledata
  except (NameError, KeyError):
    raise seash_exceptions.ModuleImportError("Module '" + modulefn + "' is not well defined")
  finally:
    # Remove the module path from the pythonpath because we don't need it anymore
    sys.path = sys.path[1:]


def import_all_modules():
  """
  <Purpose>
    Imports all modules within the modules folder.  This should only be called once 
    throughout the entire execution of seash.
      
  <Side Effects>
    Modules that don't have collisions will have their commanddicts and 
    helptexts loaded and returned.
    
  <Exceptions>
    ImportError: There is an existing module with the same name already imported.
      
  <Return>
    The seashcommanddict that contains the imported commands on top of the 
    passed in commanddict.

  """
  for module_folder in os.listdir(MODULES_FOLDER_PATH): 
    if os.path.isfile(MODULES_FOLDER_PATH + os.sep + module_folder):
      continue
    
    try:
      if module_folder in module_data:
        raise seash_exceptions.ModuleImportError("Module already imported")
      module_data[module_folder] = import_module(module_folder)
    except seash_exceptions.ModuleImportError, e:
      print str(e)




def ensure_no_conflicts_in_commanddicts(originaldict, comparedict):
  """
  <Purpose>
    Recursively compares two commanddicts to see if they have conflicting commands.
    
  <Arguments>
    originaldict: A commanddict to compare.
    comparedict: A commanddict to compare.
    
  <Side Effects>
    None
    
  <Exceptions>
    ModuleConflictError - A command was conflicting.  
        The error detail is the problematic command.
    
  <Returns>
    None
  """
  
  """
  Child nodes are identical if they all of the following are identical: 
    helptext/callback/summary.
     
  There are 3 cases we have to worry about.
  > Shared child node.
    > Child nodes are identical.  Check grandchildren.
    > Only one is defined.  Check grandchildren.
    > Both child nodes are defined and are not identical.  Reject.
  > Node is not shared.  Accept. 
  """
  
  for child in comparedict.keys():
    # Node not shared.
    if child not in originaldict:
      continue
    
    # Shared node
    comparechild_defined = is_commanddictnode_defined(comparedict[child])
    originalchild_defined = is_commanddictnode_defined(originaldict[child])
    
    # Only one is defined, or;
    # both are defined and they are identical
    if ((comparechild_defined ^ originalchild_defined) or
        (comparechild_defined and originalchild_defined and 
         comparedict[child]['callback'] == comparedict[child]['callback'] and 
         comparedict[child]['help_text'] == comparedict[child]['help_text'] and
         comparedict[child]['summary'] == comparedict[child]['summary'])):
      try:
        ensure_no_conflicts_in_commanddicts(comparedict[child]['children'], originaldict[child]['children'])
      except seash_exceptions.ModuleConflictError, e:
        # Reconstruct the full command recursively
        raise seash_exceptions.ModuleConflictError(child + " " + str(e))
      continue
    
    # Not identical.  Conflict found.
    raise seash_exceptions.ModuleConflictError(child)


def is_commanddictnode_defined(node):
  """
  A child node is defined if it has either a helptext/callback/summary.
  If a node's callback is None it can still be undefined. 
  """
  return (('callback' in node and not node['callback'] is None) or
           'help_text' in node or
           'summary' in node)


def are_cmddicts_same(dict1, dict2):
  """ 
  Checks to see if two cmddicts are the same.
  Two cmddicts are defined to be the same if they have the same callbacks/
  helptexts/children/summaries for all nodes. 
  """
  
  # If the set of all keys are not the same, they must not be the same.
  if set(dict1.keys()) != set(dict2.keys()):
    return False
  
  # Everything in dict1 should be in dict2
  for key in dict1:
    # Check everything except children;  Check for children recursively
    for propertytype in dict1[key]:
      if (not propertytype in dict2[key] or
          dict1[key][propertytype] != dict2[key][propertytype]):
        return False
      
    # Check children
    if not are_cmddicts_same(dict1[key]['children'], dict2[key]['children']):
      return False
      
  return True


def merge_commanddict_recursive(originaldict, mergedict):
  """
  <Purpose> 
    Recursively merge mergedict into originaldict.
    We assume that there are no conflicting modules here.  
    Be sure to check that there aren't any collisions!
    
  <Arguments>
    originaldict: The commanddict to merge to.
    mergedict: The commanddict to merge from.
  
  <Side Effects>
    Originaldict will contain all command entries in mergedict.
    
  <Exceptions>
    There shouldn't be any...
    
  <Return>
    None
  """
  
  """
  Every command in the mergedict should be placed into the original.  
  We do not handle the case where a shared node is defined on both sides.
  That check is done by ensure_no_conflicts_in_commanddict().
  We make a deep copy of mergedict to make the deletion case easier.
  """
  for commandnode in mergedict:
    # Trivial case
    if commandnode not in originaldict:
      originaldict[commandnode] = deepcopy(mergedict[commandnode])
    
    else:
      # Shared node exists in original but is not defined
      # Replace properties if they exist, and then merge over the children.
      if not is_commanddictnode_defined(originaldict[commandnode]):
        for entry in mergedict[commandnode]:
          if entry != 'children':
            originaldict[commandnode][entry] = mergedict[commandnode][entry]
      
      merge_commanddict_recursive(originaldict[commandnode]['children'], mergedict[commandnode]['children'])
    
    
      

def merge_commanddict(originaldict, mergedict):
  """
  <Purpose>
    Merges two command dictionaries.  This is used to add commands to the main
    seash commanddict.  Remember to perform the same call on under the help node 
    so that the help command works as expected.
    
    e.g.
      merge_commanddict(seashcommanddict, mycommanddict)
      merge_commanddict(seashcommanddict['help']['children'], mycommanddict) 
    
  <Arguments>
    cmddict_original: The commanddict to merge to.
    cmddict_merge: The commanddict from which to merge commands from.
    
  <Side Effects>
    All commands from cmddict_merge will be merged into cmddict_original.
    This assumes that all commands are not conflicting.  If they are, an exception is raised.
    
  <Exceptions>
    ModuleConflictError: A conflicting command was found.
  
  <Returns>
    None
  """
  
  ensure_no_conflicts_in_commanddicts(originaldict, mergedict)
  merge_commanddict_recursive(originaldict, mergedict)


def remove_commanddict(originaldict, removedict):
  """
  <Purpose>
    Removes all commands found in a command dictionary from another command 
    dictionary. Remember to perform the same call on under the help node 
    so that the help command works as expected.
    
    e.g.
      remove_commanddict(seashcommanddict, mycommanddict)
      remove_commanddict(seashcommanddict['help']['children'], mycommanddict) 
    
  <Arguments>
    originaldict: The commanddict to remove from.
    removedict: The commanddict containing the commands to remove.
    
  <Side Effects>
    All commands in cmddict_merge will be removed from originaldict.
    A node will not be removed while there are children under that node.
    However, if a parent node is undefined and the last defined child is removed,
    that parent node will be removed as well.
    
  <Exceptions>
    None
  
  <Returns>
    None
  """
  
  for child in removedict:
    if child in originaldict:
      # Recursively remove all children specified
      remove_commanddict(originaldict[child]['children'], removedict[child]['children'])
      # Remove the definition as well if it is defined in removedict
      if is_commanddictnode_defined(removedict[child]):
        # Remove everything except for children.  We remove those recursively.
        for propertytype in removedict[child]:
          if propertytype != 'children':
            del originaldict[child][propertytype]
      # Remove this node if this node is no longer defined, and if there are no 
      # remaining child nodes.
      if not (is_commanddictnode_defined(originaldict[child]) or originaldict[child]['children']):
        del originaldict[child]


def enable(commanddict, modulename):
  """
  <Purpose>
    Enables a module and imports its commands into the seash commanddict.

  <Arguments>
    modulename: The module to import.

  <Side Effects>
    All commands inside the specified module will be inserted into the seash
    commanddict if possible.

    The file modulename.disabled will be removed from /modules/ indicating that
    this module has been enabled.

  <Exceptions>
    Exceptions raised by merge_commanddict()

  <Returns>
    None
  """
  # Is this an installed module?
  if not modulename in module_data:
    raise seash_exceptions.UserError("Error, module '"+modulename+"' is not installed")

  if _is_module_enabled(modulename):
    raise seash_exceptions.UserError("Module is already enabled.")

  merge_commanddict(commanddict, module_data[modulename]['command_dict'])

  try:
    # We mark this module as enabled by deleting the modulename.disabled file
    os.remove(MODULES_FOLDER_PATH + os.sep + modulename + ".disabled") 
  except OSError, e:
    # If the file was deleted before we were able to delete it, it should not
    # be a problem.
    if not "cannot find the file" in str(e):
      raise


def disable(commanddict, modulename):
  """
  <Purpose>
    Disables a module and removes its commands from the seash commanddict.

  <Arguments>
    modulename: The module to disable.

  <Side Effects>
    All commands inside the specified module will be removed from the seash
    commanddict.

    A file (modulename.disabled) will be created under /modules/ indicating that
    this module has been disabled.

  <Exceptions>
    Exceptions raised by merge_commanddict()

  <Returns>
    None
  """
  # Is this an installed module?
  if not modulename in module_data:
    raise seash_exceptions.UserError("Error, module '"+modulename+"' is not installed")
  
  # Is this module enabled?
  if not _is_module_enabled(modulename):
    raise seash_exceptions.UserError("Module is not enabled.")

  remove_commanddict(commanddict, module_data[modulename]['command_dict'])

  # We mark this module as disabled by adding a modulename.disabled file.
  open(MODULES_FOLDER_PATH + os.sep + modulename + ".disabled", 'w')


def _is_module_enabled(modulename):
  """
  A module is enabled if there is not a "modulename.disabled" file under the /modules
  folder.
  """
  disabled_filename = modulename + '.disabled'
  return not disabled_filename in os.listdir('./modules/')


def get_enabled_modules():
  """
  <Purpose>
    Returns all enabled modules.
  <Arguments>
    None
  <Side Effects>
    None
  <Exceptions>
    None
  <Return>
    The list of all enabled modules.
  """
  enabled = []
  directory_contents = os.listdir('./modules/')
  for fname in directory_contents:
    if (os.path.isdir('./modules/'+fname) and 
        not fname+'.disabled' in directory_contents):
      enabled.append(fname)
  return enabled


def enable_modules_from_last_session(seashcommanddict):
  """
  Enable every module that isn't marked as disabled in the modules folder.
  This function is meant to be called when seash is initializing and nowhere
  else.  A module is marked as disabled when there is a modulename.disabled 
  file.
  """
  modules_to_enable = get_enabled_modules()
  for modulename in modules_to_enable:
    # There are no bad side effects to seash's state when we do this
    # The only thing that should happen is that the modulename.disabled file
    # gets created (temporarily)
    disable(seashcommanddict, modulename)
    enable(seashcommanddict, modulename)
  
  modules_to_enable.sort()
  
  print 'Enabled modules:', ', '.join(modules_to_enable)
  print "To see a list of all available modules, use the 'show modules' command."


def preprocess_input(userinput):
  """
  <Purpose>
    Preprocess the raw command line input string.

  <Arguments>
    The raw command line input string.  We assume it is pre-stripped.

  <Side Effects>
    The string will be processed by each module that has a defined preprocessor.

  <Exceptions>
    None

  <Returns>
    The preprocessed string.
  """
  for module in get_enabled_modules():
    # Not every module has a preprocessor...
    if 'input_preprocessor' in module_data[module]:
      userinput = module_data[module]['input_preprocessor'](userinput)
  return userinput


def _attach_module_identifier(command_dict, modulefn):
  """
  Attaches a 'module': modulename entry to each node in the dictionary.
  This is used by the help printer so that the user can tell if a command was
  included by default or via a module. 
  """
  for command in command_dict:
    command_dict[command]['module'] = modulefn
    _attach_module_identifier(command_dict[command]['children'], modulefn)

import_all_modules()