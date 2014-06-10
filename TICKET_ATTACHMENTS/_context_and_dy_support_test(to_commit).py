from repyportability import *
import repyhelper
_context = locals()

# Add dylink support
repyhelper.translate_and_import("dylink.repy", callfunc = 'initialize')
# the dy_* functions are not added to the namespace. I am unsure whether we need to pass in _context, or any dict is fine.
init_dylink(_context,{})
# Make our own `dy_import_module_symbols` that is based on `dy_import_module`, and then adds it to the context.
# It is not currently possible to use the real one (see ticket #1046 )
def _dy_import_module_symbols(module,new_callfunc="import"):
  temp = dy_import_module(module, new_callfunc)
  for x in temp._context:  # Copy in new functions into our namespace. Collisions do not replace.
    if x not in _context: #Prevents imported object from destroying our namespace.
      _context[x] = temp._context[x]
      
dy_import_module_symbols = _dy_import_module_symbols