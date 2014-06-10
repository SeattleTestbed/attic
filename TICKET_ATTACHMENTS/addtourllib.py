def urllib_unquote_parameters(string):
  """
  <Purpose>
    Unencode a sring of query string or posted data to a dictionary with a key and value

  <Arguments>
    string:
           The string to unquote.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The unquoted dictionary.
  """
  unquotedstr = urllib_unquote(string)
  
  list_qs = unquotedstr.split('&')
  
  unquoted_keyvals = {}
  for single_qs in list_qs:
    [key, val] = single_qs.split('=')
    unquoted_keyvals[key] = val    

  return unquoted_keyvals
