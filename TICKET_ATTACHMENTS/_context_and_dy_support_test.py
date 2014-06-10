from repyportability import *
import repyhelper
_context = locals()

# The first issue is that even after being 'imported', the dylink functions are not available
# The default callfunc is 'import'. dylink requires initialize.
repyhelper.translate_and_import("dylink.repy", callfunc = 'initialize')

# Next. Even though it runs correctly, the dy_* functions are not added to the namespace.

# If we pass in our current `_context` `dy_import_module_symbols` complains that our context isn't safe.
# Yet at the same time, whichever `context` is passed in here is the one dy_import_module_symbols does its import into.
# So passing in anything besides our `_context` wouldn't make functions available into the current context (ala `from x import *`).

# Possible solutions:
#   Check feasability with other import calls - is this a problem with all of them, or only `dy_import_module_symbols`.
#   Change safety check to happen somewhere else.
#   rewrite our own dy_import_module_symbols, and then there won't be a safety check.
init_dylink(_context,{})

# Make our own `dy_import_module_symbols` that is based on `dy_import_module`, and then adds it to the context.
def _dy_import_module_symbols(module,new_callfunc="import"):
  temp = dy_import_module(module, new_callfunc)
  for x in temp._context.keys():  # Copy in new functions into our namespace. Collisions do not replace.
    if x not in _context: #Prevents imported object from destroying our namespace.
      _context[x] = temp._context[x]

dy_import_module_symbols = _dy_import_module_symbols

# Now we should be able to call `dy_import_module_symbols` without any problems.
dy_import_module_symbols('advertise.repy')
print dir()
