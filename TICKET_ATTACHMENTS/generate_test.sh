#!/bin/sh
tests=`ls | grep "ut_repyv2api.*py$" | grep -v "_py"`
for i in $tests ; do
  echo "\nTest:" $i
  python -c "import repyhelper; repyhelper.translate_and_import('$i')"
done
