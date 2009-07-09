# file.next() on a write-enabled file should raise IOError

if callfunc == "initialize":
  fobj = open("junk_test.out", 'r+')
  try:
    fobj.next()
  except IOError:
    pass
  else:
    raise Exception('Supposed to throw exception!')
  finally:
    fobj.close()
