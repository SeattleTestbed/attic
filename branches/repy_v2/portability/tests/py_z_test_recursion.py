"""
Author: Andreas Sekine
Description:
  Perform various tests on recursive/circular includes/imports/translates
  
  Uses files of the form rhtestrecursion_n.r2py
  
  No output indicates success
  
"""

TESTFILES = ['rhtestrecursion_1.r2py', 'rhtestrecursion_2.r2py', 'rhtestrecursion_3.r2py', 'rhtestrecursion_4.r2py']


import repyhelper
import test_utils

test_utils.cleanup_translations(TESTFILES)

#This tests circular includes
translation = repyhelper.translate(TESTFILES[0])
if translation == "":
  print "Error translating circular recursion"
else:
  #actually include it to make sure the translation was valid
  mod = __import__(translation)
 
test_utils.cleanup_translations(TESTFILES)
  
  
#Tests self include  
translation = repyhelper.translate(TESTFILES[-1])
if translation == "":
  print "Error translating self-include"
else:
  mod2 = __import__(translation)
