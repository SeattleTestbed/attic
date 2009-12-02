"""
This tests arguments with circular references passed through the namespace
which need to be carefully copied by NamespaceAPIFunctionWrapper._copy().
"""

import namespace


def foo(testarg):
  return testarg


def noop(*args, **kwargs):
  pass


foo_func_dict = {
  'target_func' : foo,
  'arg_checking_func' : noop,
  'return_checking_func' : noop,
}

foo_wrapper_obj = namespace.NamespaceAPIFunctionWrapper(foo_func_dict)

wrapped_foo = foo_wrapper_obj.wrapped_function

# List with circular references.
circlist = []
circlist.append(circlist)
retval = wrapped_foo(circlist)
# Make sure that the retval is not the original argument and that the retval
# has circular references like the original argument.
assert(retval is not circlist)
assert(retval[0] is retval)

# Dict with circular references.
circdict = {}
circdict["test"] = circdict
retval = wrapped_foo(circdict)
# Make sure that the retval is not the original argument and that the retval
# has circular references like the original argument.
assert(retval is not circdict)
assert(retval["test"] is retval)

# Tuple with circular references. Note that I don't believe it's possible to
# have a tuple with directly circular references, but instead only indirectly
# through other objects in the tuple such as other lists and dicts.
mydict = {}
circtuple = (mydict,)
mydict["test"] = circtuple
retval = wrapped_foo(circtuple)
# Make sure that the retval is not the original argument and that the retval
# has circular references like the original argument.
assert(retval is not circtuple)
assert(retval[0]["test"] is retval)

